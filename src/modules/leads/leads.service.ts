import { LeadStatus, LobVerificationStatus, NotificationEventType, type Prisma } from "@prisma/client";

import { prisma } from "../../db/client";
import { serializeLead } from "../../shared/utils/leadSerializer";
import { apiLeadStatusToDb } from "../../shared/utils/statusMappings";
import { AppError } from "../../shared/middleware/errorHandler";
import { queueLetterDispatch } from "../../jobs/letterDispatch.job";

type Operator = { id: string; name: string; role: "admin" | "reviewer" };
type LeadWithRelations = Prisma.LeadGetPayload<{ include: { mailEvents: true; activityLogs: true } }>;

async function fetchLeadOrThrow(id: string): Promise<LeadWithRelations> {
  const lead = await prisma.lead.findUnique({
    where: { id },
    include: { mailEvents: { orderBy: { timestamp: "asc" } }, activityLogs: { orderBy: { timestamp: "asc" } } },
  });
  if (!lead) throw new AppError("Lead not found", 404);
  return lead;
}

function checkApproveCompliance(lead: {
  status: LeadStatus;
  lobVerificationStatus: LobVerificationStatus;
  manualReviewRequired: boolean;
  flaggedForLegalReview: boolean;
  legalReviewCleared: boolean;
}) {
  if (lead.status !== "PENDING_APPROVAL") throw new AppError("status must be pendingApproval", 400);
  if (!["VERIFIED", "CORRECTED"].includes(lead.lobVerificationStatus)) {
    throw new AppError("lob_verification_status must be verified or corrected", 400);
  }
  if (lead.manualReviewRequired) throw new AppError("manual_review_required must be false", 400);
  if (lead.flaggedForLegalReview && !lead.legalReviewCleared) throw new AppError("legal review must be cleared", 400);
}

export async function listLeads(filters: {
  state?: "CA" | "FL";
  county?: string;
  status?: string;
  page?: number;
  page_size?: number;
}) {
  const where: Prisma.LeadWhereInput = {};
  if (filters.state) where.state = filters.state;
  if (filters.county) where.county = filters.county;
  if (filters.status) {
    const mapped = apiLeadStatusToDb(filters.status);
    if (!mapped) throw new AppError("Invalid status filter", 400);
    where.status = mapped;
  }

  const page = Math.max(filters.page ?? 1, 1);
  const pageSize = Math.min(Math.max(filters.page_size ?? 50, 1), 200);
  const rows = await prisma.lead.findMany({
    where,
    orderBy: { createdAt: "desc" },
    skip: (page - 1) * pageSize,
    take: pageSize,
    include: { mailEvents: true, activityLogs: true },
  });
  return rows.map(serializeLead);
}

export async function getLead(id: string) {
  return serializeLead(await fetchLeadOrThrow(id));
}

export async function approveLead(id: string, operator: Operator) {
  const lead = await prisma.lead.findUnique({ where: { id } });
  if (!lead) throw new AppError("Lead not found", 404);
  checkApproveCompliance(lead);

  await prisma.$transaction(async (tx) => {
    await tx.lead.update({ where: { id }, data: { status: "APPROVED" } });
    await tx.activityLog.create({
      data: { leadId: id, action: "Letter approved for mailing", operatorId: operator.id, operatorName: operator.name },
    });
    await tx.notificationEvent.create({
      data: {
        type: NotificationEventType.APPROVAL_COMPLETED,
        leadId: id,
        leadOwnerName: lead.ownerName,
        message: "Approval completed",
      },
    });
  });

  await queueLetterDispatch(id);
  return getLead(id);
}

export async function rejectLead(id: string, operator: Operator, reason?: string) {
  const lead = await prisma.lead.findUnique({ where: { id } });
  if (!lead) throw new AppError("Lead not found", 404);
  if (["SENT", "DELIVERED", "RETURNED"].includes(lead.status)) {
    throw new AppError("Cannot reject after sent lifecycle begins", 400);
  }

  await prisma.$transaction(async (tx) => {
    await tx.lead.update({ where: { id }, data: { status: "IMPORTED", rejectionReason: reason ?? null } });
    await tx.activityLog.create({
      data: {
        leadId: id,
        action: "Letter rejected",
        operatorId: operator.id,
        operatorName: operator.name,
        note: reason ?? null,
      },
    });
  });
  return getLead(id);
}

export async function holdLead(id: string, operator: Operator, reason?: string) {
  const lead = await prisma.lead.findUnique({ where: { id } });
  if (!lead) throw new AppError("Lead not found", 404);

  await prisma.$transaction(async (tx) => {
    await tx.lead.update({ where: { id }, data: { status: "ON_HOLD" } });
    await tx.activityLog.create({
      data: {
        leadId: id,
        action: "Letter placed on hold",
        operatorId: operator.id,
        operatorName: operator.name,
        note: reason ?? null,
      },
    });
  });
  return getLead(id);
}

export async function clearLegalReview(id: string, operator: Operator, legalReviewCleared = true) {
  if (operator.role !== "admin") throw new AppError("Only admin can clear legal review", 403);
  const lead = await prisma.lead.findUnique({ where: { id } });
  if (!lead) throw new AppError("Lead not found", 404);
  if (!lead.flaggedForLegalReview) throw new AppError("Lead is not flagged for legal review", 400);

  await prisma.$transaction(async (tx) => {
    await tx.lead.update({ where: { id }, data: { legalReviewCleared, manualReviewRequired: false } });
    await tx.activityLog.create({
      data: { leadId: id, action: "Legal review cleared", operatorId: operator.id, operatorName: operator.name },
    });
  });
  return getLead(id);
}

export async function saveNotes(id: string, notes: string) {
  const lead = await prisma.lead.findUnique({ where: { id } });
  if (!lead) throw new AppError("Lead not found", 404);
  await prisma.lead.update({ where: { id }, data: { notes, updatedAt: new Date() } });
  return getLead(id);
}

export async function getTrackingEvents(leadId: string) {
  const lead = await prisma.lead.findUnique({ where: { id: leadId } });
  if (!lead) throw new AppError("Lead not found", 404);
  const rows = await prisma.mailEvent.findMany({
    where: { leadId },
    orderBy: { timestamp: "desc" },
  });
  return rows.map((row) => ({
    event: row.event,
    timestamp: row.timestamp.toISOString(),
    description: row.description,
  }));
}

export async function listLetterQueue(filters: {
  state?: "CA" | "FL";
  county?: string;
  status?: string;
  page?: number;
  page_size?: number;
}) {
  const q = { ...filters };
  if (!q.status) {
    q.status = "pendingApproval";
  }
  return listLeads(q);
}
