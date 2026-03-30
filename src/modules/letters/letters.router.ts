import type { FastifyInstance } from "fastify";
import { z } from "zod";

import { requireAuth } from "../../shared/middleware/auth";
import { prisma } from "../../db/client";
import { AppError } from "../../shared/middleware/errorHandler";
import { dispatchLobLetter, renderOutreachLetter } from "./letter.service";
import { listLetterQueue } from "../leads/leads.service";

const lettersQueueQuerySchema = z.object({
  state: z.enum(["CA", "FL"]).optional(),
  county: z.string().optional(),
  status: z.string().optional(),
  page: z.coerce.number().int().positive().default(1),
  page_size: z.coerce.number().int().positive().max(200).default(50),
});

export async function lettersRouter(app: FastifyInstance): Promise<void> {
  app.get("/letters/queue", { preHandler: [requireAuth] }, async (_request, reply) => {
    const q = lettersQueueQuerySchema.parse(_request.query);
    return reply.send(await listLetterQueue(q));
  });

  app.post("/letters/:id/dispatch", { preHandler: [requireAuth] }, async (request, reply) => {
    const id = String((request.params as { id: string }).id);
    const lead = await prisma.lead.findUnique({ where: { id } });
    if (!lead) throw new AppError("Lead not found", 404);
    const html = renderOutreachLetter(lead);
    const out = await dispatchLobLetter(lead, html);
    await prisma.lead.update({ where: { id }, data: { lobLetterId: out.id, status: "SENT" } });
    return reply.send({ id: out.id });
  });
}
