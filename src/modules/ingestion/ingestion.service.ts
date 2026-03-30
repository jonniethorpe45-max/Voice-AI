import type { FastifyInstance } from "fastify";
import { NotificationEventType, type Prisma, type StateAbbr } from "@prisma/client";

import { prisma } from "../../db/client";
import { queueAddressVerification } from "../../jobs/addressVerification.job";
import { notificationsService } from "../notifications/notifications.service";
import type { CountyAdapter, IngestedLead } from "./adapters/types";
import { losAngelesAdapter } from "./adapters/losAngeles.adapter";
import { orangeAdapter } from "./adapters/orange.adapter";
import { elDoradoAdapter } from "./adapters/elDorado.adapter";
import { tulareAdapter } from "./adapters/tulare.adapter";
import { leeAdapter } from "./adapters/lee.adapter";
import { brevardAdapter } from "./adapters/brevard.adapter";

const ADAPTERS: CountyAdapter[] = [losAngelesAdapter, orangeAdapter, elDoradoAdapter, tulareAdapter, leeAdapter, brevardAdapter];

function titleCaseAddress(value: string): string {
  return value.trim().toLowerCase().split(" ").filter(Boolean).map((p) => p[0].toUpperCase() + p.slice(1)).join(" ");
}

function assignmentConfidence(lead: IngestedLead): number {
  let score = 0;
  if (lead.surplus_amount > 10000) score += 0.3;
  if (lead.mailing_address.trim().toLowerCase() !== lead.property_address.trim().toLowerCase()) score += 0.2;
  const owner = lead.owner_name.toUpperCase();
  if (!owner.includes("LLC") && !owner.includes("CORP") && !owner.includes("TRUST")) score += 0.2;
  if (lead.surplus_amount > 50000) score += 0.2;
  return Math.min(score, 1);
}

async function persistLead(tx: Prisma.TransactionClient, county: string, state: StateAbbr, item: IngestedLead) {
  if (item.surplus_amount <= 0) return null;
  const parcelNumber = item.parcel_number.trim();
  const existing = await tx.lead.findFirst({ where: { parcelNumber, county }, select: { id: true } });
  if (existing) return null;

  const isFlorida = state === "FL";
  const lead = await tx.lead.create({
    data: {
      parcelNumber,
      ownerName: item.owner_name.trim(),
      propertyAddress: titleCaseAddress(item.property_address),
      mailingAddress: titleCaseAddress(item.mailing_address),
      city: titleCaseAddress(item.city),
      county,
      state,
      zip: item.zip.trim(),
      surplusAmount: item.surplus_amount,
      saleDate: new Date(item.sale_date),
      status: "IMPORTED",
      dataSource: `${county} County Source`,
      sourceUrl: item.source_url,
      sourceSnapshot: item.source_snapshot as Prisma.InputJsonValue,
      assignmentConfidence: assignmentConfidence(item),
      manualReviewRequired: isFlorida,
      flaggedForLegalReview: isFlorida,
      legalReviewCleared: false,
    },
  });

  await tx.activityLog.create({ data: { leadId: lead.id, action: "Lead imported", operatorName: "system", note: "Ingested from county source" } });
  await notificationsService.create({ type: NotificationEventType.NEW_LEAD_READY, leadId: lead.id, leadOwnerName: lead.ownerName, message: `New lead ready from ${lead.county}, ${lead.state}` });
  await queueAddressVerification(lead.id);
  return lead;
}

export async function runAdapter(adapter: CountyAdapter) {
  const run = await prisma.ingestionRun.create({ data: { county: adapter.county, state: adapter.state, status: "running" } });
  try {
    const rows = await adapter.run();
    let added = 0;
    await prisma.$transaction(async (tx) => {
      for (const item of rows) {
        // eslint-disable-next-line no-await-in-loop
        const created = await persistLead(tx, adapter.county, adapter.state, item);
        if (created) added += 1;
      }
    });

    return prisma.ingestionRun.update({ where: { id: run.id }, data: { status: "completed", leadsFound: rows.length, leadsAdded: added, completedAt: new Date() } });
  } catch (error) {
    return prisma.ingestionRun.update({ where: { id: run.id }, data: { status: "failed", error: error instanceof Error ? error.message : "Unknown ingestion error", completedAt: new Date() } });
  }
}

export async function runAllIngestion(state?: StateAbbr) {
  const target = state ? ADAPTERS.filter((a) => a.state === state) : ADAPTERS;
  const out = [];
  for (const adapter of target) {
    // eslint-disable-next-line no-await-in-loop
    out.push(await runAdapter(adapter));
  }
  return out;
}

export async function ingestionRouter(app: FastifyInstance): Promise<void> {
  app.post("/ingestion/run", async (_request, reply) => {
    return reply.send({ runs: await runAllIngestion() });
  });
}
