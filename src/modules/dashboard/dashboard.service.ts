import { LeadStatus } from "@prisma/client";

import { prisma } from "../../db/client";
import { redis } from "../../jobs/queues";
import { dbLeadStatusToApi } from "../../shared/utils/statusMappings";
import { APP } from "../../config/app";

const CACHE_KEY = "dashboard:stats:v1";
const TTL_SECONDS = APP.dashboardCacheTtlSeconds;

export async function getDashboardStats() {
  const cached = await redis.get(CACHE_KEY);
  if (cached) return JSON.parse(cached);

  const [total, pending, flagged, sent, delivered, returned, agg, byState, byStatus] = await Promise.all([
    prisma.lead.count(),
    prisma.lead.count({ where: { status: "PENDING_APPROVAL" } }),
    prisma.lead.count({ where: { flaggedForLegalReview: true } }),
    prisma.lead.count({ where: { status: "SENT" } }),
    prisma.lead.count({ where: { status: "DELIVERED" } }),
    prisma.lead.count({ where: { status: "RETURNED" } }),
    prisma.lead.aggregate({ _sum: { surplusAmount: true }, _avg: { surplusAmount: true } }),
    prisma.lead.groupBy({ by: ["state"], _count: { _all: true }, _sum: { surplusAmount: true } }),
    prisma.lead.groupBy({ by: ["status"], _count: { _all: true } }),
  ]);

  const leads_by_state: Record<"CA" | "FL", { count: number; total_surplus: number }> = {
    CA: { count: 0, total_surplus: 0 },
    FL: { count: 0, total_surplus: 0 },
  };
  byState.forEach((row) => {
    leads_by_state[row.state] = { count: row._count._all, total_surplus: Number(row._sum.surplusAmount ?? 0) };
  });

  const leads_by_status: Record<string, number> = {
    imported: 0,
    addressVerified: 0,
    letterGenerated: 0,
    pendingApproval: 0,
    onHold: 0,
    approved: 0,
    sent: 0,
    delivered: 0,
    returned: 0,
    failed: 0,
  };
  byStatus.forEach((row) => {
    leads_by_status[dbLeadStatusToApi(row.status as LeadStatus)] = row._count._all;
  });

  const payload = {
    total_leads: total,
    pending_approval: pending,
    flagged_legal_review: flagged,
    letters_sent: sent,
    letters_delivered: delivered,
    letters_returned: returned,
    total_surplus_amount: Number(agg._sum.surplusAmount ?? 0),
    average_surplus_amount: Number(agg._avg.surplusAmount ?? 0),
    leads_by_state,
    leads_by_status,
    generated_at: new Date().toISOString(),
  };

  await redis.set(CACHE_KEY, JSON.stringify(payload), "EX", TTL_SECONDS);
  return payload;
}
