import bcrypt from "bcryptjs";
import { PrismaClient, Role, LeadStatus, NotificationEventType } from "@prisma/client";

const prisma = new PrismaClient();

function pickStatus(i: number): LeadStatus {
  const statuses: LeadStatus[] = [
    "IMPORTED", "ADDRESS_VERIFIED", "LETTER_GENERATED", "PENDING_APPROVAL", "ON_HOLD",
    "APPROVED", "SENT", "DELIVERED", "RETURNED", "FAILED",
  ];
  return statuses[i % statuses.length];
}

async function seedUsers() {
  const adminHash = await bcrypt.hash("Admin1234!", 10);
  const reviewerHash = await bcrypt.hash("Review1234!", 10);

  const admin = await prisma.user.upsert({
    where: { email: "admin@taxdeeds.local" },
    update: { name: "Admin User", role: Role.ADMIN, passwordHash: adminHash },
    create: { email: "admin@taxdeeds.local", name: "Admin User", role: Role.ADMIN, passwordHash: adminHash },
  });

  const reviewer = await prisma.user.upsert({
    where: { email: "reviewer@taxdeeds.local" },
    update: { name: "Reviewer User", role: Role.REVIEWER, passwordHash: reviewerHash },
    create: { email: "reviewer@taxdeeds.local", name: "Reviewer User", role: Role.REVIEWER, passwordHash: reviewerHash },
  });

  return { admin, reviewer };
}

async function makeLead(county: string, state: "CA" | "FL", idx: number, owner: string) {
  const status = pickStatus(idx);
  const isFlorida = state === "FL";
  const lead = await prisma.lead.create({
    data: {
      parcelNumber: `${county.replace(/\s+/g, "").toUpperCase()}-${idx.toString().padStart(4, "0")}`,
      ownerName: owner,
      ownerPhone: idx % 3 === 0 ? `(555) 100-${idx.toString().padStart(4, "0")}` : null,
      ownerEmail: idx % 4 === 0 ? `owner${idx}@example.com` : null,
      propertyAddress: `${100 + idx} Main St`,
      mailingAddress: idx % 2 === 0 ? `${200 + idx} Market St` : `${100 + idx} Main St`,
      city: county,
      county,
      state,
      zip: state === "CA" ? "90001" : "33901",
      surplusAmount: (8000 + idx * 1500) as any,
      saleDate: new Date(Date.now() - idx * 86400000),
      status,
      lobVerificationStatus: idx % 2 === 0 ? "VERIFIED" : "CORRECTED",
      lobAddressId: idx % 2 === 0 ? `adr_${idx}` : null,
      lobLetterId: ["SENT", "DELIVERED", "RETURNED"].includes(status) ? `ltr_${idx}` : null,
      manualReviewRequired: isFlorida,
      legalReviewCleared: !isFlorida,
      flaggedForLegalReview: isFlorida,
      assignmentConfidence: Math.min(1, 0.3 + idx * 0.03),
      dataSource: `${county} County Source`,
      sourceUrl: "https://example.com/source",
      notes: `Seed note ${idx}`,
      sourceSnapshot: { idx, county, state },
    },
  });

  await prisma.activityLog.create({
    data: {
      leadId: lead.id,
      action: "Lead imported",
      operatorName: "system",
      note: `Initial status: ${status}`,
    },
  });

  if (["SENT", "DELIVERED", "RETURNED"].includes(status)) {
    await prisma.mailEvent.create({
      data: {
        leadId: lead.id,
        event: "submitted",
        description: "Submitted to Lob",
        timestamp: new Date(),
      },
    });
  }
  if (status === "DELIVERED") {
    await prisma.mailEvent.create({
      data: { leadId: lead.id, event: "delivered", description: "Delivered", timestamp: new Date() },
    });
  }
  if (status === "RETURNED") {
    await prisma.mailEvent.create({
      data: { leadId: lead.id, event: "returned", description: "Returned", timestamp: new Date() },
    });
  }
}

async function seedLeads() {
  const plan: Array<{ county: string; state: "CA" | "FL"; count: number }> = [
    { county: "Los Angeles", state: "CA", count: 10 },
    { county: "Orange", state: "CA", count: 6 },
    { county: "El Dorado", state: "CA", count: 4 },
    { county: "Tulare", state: "CA", count: 4 },
    { county: "Lee", state: "FL", count: 3 },
    { county: "Brevard", state: "FL", count: 3 },
  ];

  let i = 1;
  for (const p of plan) {
    for (let j = 0; j < p.count; j += 1) {
      // eslint-disable-next-line no-await-in-loop
      await makeLead(p.county, p.state, i, `Owner ${i}`);
      i += 1;
    }
  }
}

async function seedNotifications() {
  const leads = await prisma.lead.findMany({ take: 5, orderBy: { createdAt: "desc" } });
  const types: NotificationEventType[] = [
    "NEW_LEAD_READY",
    "LETTER_RETURNED",
    "RECIPIENT_RESPONDED",
    "LEGAL_REVIEW_REQUIRED",
    "APPROVAL_COMPLETED",
  ];
  for (let i = 0; i < Math.min(leads.length, 5); i += 1) {
    const lead = leads[i];
    // eslint-disable-next-line no-await-in-loop
    await prisma.notificationEvent.create({
      data: {
        type: types[i],
        leadId: lead.id,
        leadOwnerName: lead.ownerName,
        message: `Seed notification ${i + 1}`,
        isRead: false,
      },
    });
  }
}

async function main() {
  await prisma.mailEvent.deleteMany();
  await prisma.notificationEvent.deleteMany();
  await prisma.activityLog.deleteMany();
  await prisma.lead.deleteMany();
  await prisma.refreshToken.deleteMany();
  await prisma.user.deleteMany();

  await seedUsers();
  await seedLeads();
  await seedNotifications();
}

main().finally(async () => {
  await prisma.$disconnect();
});
