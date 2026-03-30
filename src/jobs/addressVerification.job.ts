import axios from "axios";
import { Worker } from "bullmq";

import { env } from "../config/env";
import { prisma } from "../db/client";
import { addressVerificationQueue, redis } from "./queues";
import { queueLetterDispatch } from "./letterDispatch.job";

export async function processAddressVerification(input: { leadId: string }) {
  const lead = await prisma.lead.findUnique({ where: { id: input.leadId } });
  if (!lead) return;

  try {
    const response = await axios.post(
      "https://api.lob.com/v1/us_verifications",
      {
        primary_line: lead.mailingAddress,
        city: lead.city,
        state: lead.state,
        zip_code: lead.zip,
      },
      {
        auth: { username: env.LOB_API_KEY, password: "" },
        timeout: 20000,
      },
    );

    const deliverability = String(response.data?.deliverability ?? "").toLowerCase();
    const data: any = {
      lobAddressId: response.data?.id ? String(response.data.id) : null,
    };

    if (deliverability === "deliverable") {
      data.lobVerificationStatus = "VERIFIED";
      data.status = "LETTER_GENERATED";
    } else if (deliverability === "deliverable_incorrect") {
      data.lobVerificationStatus = "CORRECTED";
      data.status = "LETTER_GENERATED";
      if (response.data?.primary_line) data.mailingAddress = String(response.data.primary_line);
    } else if (deliverability === "undeliverable") {
      data.lobVerificationStatus = "UNDELIVERABLE";
      data.manualReviewRequired = true;
    } else {
      data.lobVerificationStatus = "FAILED";
      data.manualReviewRequired = true;
    }

    await prisma.lead.update({ where: { id: lead.id }, data });
    await prisma.activityLog.create({
      data: {
        leadId: lead.id,
        action: "Address verification completed",
        operatorName: "system",
        note: `deliverability=${deliverability || "unknown"}`,
      },
    });

    if (["VERIFIED", "CORRECTED"].includes(data.lobVerificationStatus)) {
      await queueLetterDispatch(lead.id, "generate-letter");
    }
  } catch (error) {
    await prisma.lead.update({ where: { id: lead.id }, data: { lobVerificationStatus: "FAILED", manualReviewRequired: true } });
    await prisma.activityLog.create({
      data: {
        leadId: lead.id,
        action: "Address verification failed",
        operatorName: "system",
        note: error instanceof Error ? error.message : "Unknown error",
      },
    });
  }
}

export const addressVerificationWorker = new Worker(
  "address-verification",
  async (job) => processAddressVerification(job.data as { leadId: string }),
  { connection: redis },
);

export async function queueAddressVerification(leadId: string) {
  await addressVerificationQueue.add("verify-address", { leadId }, { removeOnComplete: 1000, removeOnFail: 1000, attempts: 3 });
}
