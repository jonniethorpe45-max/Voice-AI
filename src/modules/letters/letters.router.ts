import type { FastifyInstance } from "fastify";

import { requireAuth } from "../../shared/middleware/auth";
import { prisma } from "../../db/client";
import { AppError } from "../../shared/middleware/errorHandler";
import { dispatchLobLetter, renderOutreachLetter } from "./letter.service";

export async function lettersRouter(app: FastifyInstance): Promise<void> {
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
