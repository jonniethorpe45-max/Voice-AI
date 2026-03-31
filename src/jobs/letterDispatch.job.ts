import { Worker } from "bullmq";

import { prisma } from "../db/client";
import { dispatchLobLetter, renderOutreachLetter } from "../modules/letters/letter.service";
import { letterDispatchQueue, redis } from "./queues";

export async function queueLetterDispatch(leadId: string, name = "dispatch") {
  await letterDispatchQueue.add(name, { leadId }, { removeOnComplete: 1000, removeOnFail: 1000, attempts: 3 });
}

export const letterDispatchWorker = new Worker(
  "letter-dispatch",
  async (job) => {
    const leadId = String(job.data.leadId);
    const lead = await prisma.lead.findUnique({ where: { id: leadId } });
    if (!lead) return;

    if (job.name === "generate-letter") {
      const html = renderOutreachLetter(lead);
      await prisma.lead.update({ where: { id: lead.id }, data: { status: "PENDING_APPROVAL", sourceSnapshot: { letter_html: html } as any } });
      await prisma.activityLog.create({ data: { leadId: lead.id, action: "Letter generated", operatorName: "system" } });
      return;
    }

    if (!["VERIFIED", "CORRECTED"].includes(lead.lobVerificationStatus)) {
      throw new Error("Compliance violation: address must be verified/corrected before dispatch.");
    }
    if (lead.manualReviewRequired) throw new Error("Compliance violation: manual_review_required must be false.");
    if (lead.state === "FL" && !lead.legalReviewCleared) throw new Error("Compliance violation: Florida lead requires legal review clearance.");

    const html = renderOutreachLetter(lead);
    const lob = await dispatchLobLetter(lead, html);

    await prisma.$transaction(async (tx) => {
      await tx.lead.update({ where: { id: lead.id }, data: { lobLetterId: lob.id, status: "SENT" } });
      await tx.mailEvent.create({ data: { leadId: lead.id, event: "submitted", timestamp: new Date(), description: "Letter submitted to Lob" } });
      await tx.activityLog.create({ data: { leadId: lead.id, action: "Letter dispatched via Lob", operatorName: "system" } });
    });
  },
  { connection: redis },
);
