import { createHmac } from "node:crypto";
import type { FastifyInstance } from "fastify";

import { env } from "../../config/env";
import { prisma } from "../../db/client";
import { notificationsService } from "../notifications/notifications.service";

function verify(payload: string, signature?: string): boolean {
  if (!env.LOB_WEBHOOK_SECRET) return true;
  if (!signature) return false;
  const expected = createHmac("sha256", env.LOB_WEBHOOK_SECRET).update(payload, "utf8").digest("hex");
  return expected === signature;
}

export async function webhookRouter(app: FastifyInstance): Promise<void> {
  app.post("/webhooks/lob", async (request, reply) => {
    const raw = typeof request.body === "string" ? request.body : JSON.stringify(request.body ?? {});
    const signature = request.headers["x-lob-signature"] as string | undefined;
    if (!verify(raw, signature)) return reply.status(400).send({ error: "Invalid webhook signature" });

    const payload = typeof request.body === "object" ? (request.body as Record<string, any>) : JSON.parse(raw);
    const eventType = String(payload.type ?? "");
    const lobLetterId = String(payload.body?.id ?? payload.data?.id ?? "");
    if (!lobLetterId) return reply.send({ received: true });

    const lead = await prisma.lead.findFirst({ where: { lobLetterId } });
    if (!lead) return reply.send({ received: true });

    const map: Record<string, { event: string; status?: "SENT" | "DELIVERED" | "RETURNED" }> = {
      "letter.mailed": { event: "mailed", status: "SENT" },
      "letter.in_transit": { event: "in_transit" },
      "letter.delivered": { event: "delivered", status: "DELIVERED" },
      "letter.returned": { event: "returned", status: "RETURNED" },
    };

    const m = map[eventType];
    if (!m) return reply.send({ received: true });

    await prisma.mailEvent.create({ data: { leadId: lead.id, event: m.event, description: eventType, rawPayload: payload as any, timestamp: new Date() } });
    if (m.status) await prisma.lead.update({ where: { id: lead.id }, data: { status: m.status } });

    if (eventType === "letter.returned") {
      await notificationsService.create({ type: "LETTER_RETURNED", leadId: lead.id, leadOwnerName: lead.ownerName, message: "Letter returned" });
    }

    return reply.send({ received: true });
  });
}
