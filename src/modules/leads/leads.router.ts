import type { FastifyInstance } from "fastify";

import { requireAuth } from "../../shared/middleware/auth";
import { clearLegalReviewSchema, listLeadsQuerySchema, notesBodySchema, reasonBodySchema } from "./leads.schema";
import { approveLead, clearLegalReview, getLead, holdLead, listLeads, rejectLead, saveNotes } from "./leads.service";

export async function leadsRouter(app: FastifyInstance): Promise<void> {
  app.get("/leads", { preHandler: [requireAuth] }, async (request, reply) => {
    const q = listLeadsQuerySchema.parse(request.query);
    return reply.send(await listLeads(q));
  });

  app.get("/leads/:id", { preHandler: [requireAuth] }, async (request, reply) => {
    const id = String((request.params as { id: string }).id);
    return reply.send(await getLead(id));
  });

  app.post("/leads/:id/approve", { preHandler: [requireAuth] }, async (request, reply) => {
    const id = String((request.params as { id: string }).id);
    return reply.send(await approveLead(id, request.user!));
  });

  app.post("/leads/:id/reject", { preHandler: [requireAuth] }, async (request, reply) => {
    const id = String((request.params as { id: string }).id);
    const body = reasonBodySchema.parse(request.body ?? {});
    return reply.send(await rejectLead(id, request.user!, body.reason));
  });

  app.post("/leads/:id/hold", { preHandler: [requireAuth] }, async (request, reply) => {
    const id = String((request.params as { id: string }).id);
    const body = reasonBodySchema.parse(request.body ?? {});
    return reply.send(await holdLead(id, request.user!, body.reason));
  });

  app.post("/leads/:id/clear-legal-review", { preHandler: [requireAuth] }, async (request, reply) => {
    const id = String((request.params as { id: string }).id);
    const body = clearLegalReviewSchema.parse(request.body ?? {});
    return reply.send(await clearLegalReview(id, request.user!, body.legal_review_cleared));
  });

  app.post("/leads/:id/notes", { preHandler: [requireAuth] }, async (request, reply) => {
    const id = String((request.params as { id: string }).id);
    const body = notesBodySchema.parse(request.body ?? {});
    return reply.send(await saveNotes(id, body.notes));
  });
}
