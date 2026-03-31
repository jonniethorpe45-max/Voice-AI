import type { FastifyInstance } from "fastify";
import { z } from "zod";

import { requireAuth } from "../../shared/middleware/auth";
import { notificationsService } from "./notifications.service";

const idParamSchema = z.object({ id: z.string().uuid() });

export async function notificationsRouter(app: FastifyInstance): Promise<void> {
  app.get("/notifications", { preHandler: [requireAuth] }, async (_req, reply) => {
    return reply.send(await notificationsService.list());
  });

  app.post("/notifications/:id/read", { preHandler: [requireAuth] }, async (request, reply) => {
    const { id } = idParamSchema.parse(request.params);
    await notificationsService.markRead(id);
    return reply.status(204).send();
  });

  app.post("/notifications/read-all", { preHandler: [requireAuth] }, async (_req, reply) => {
    await notificationsService.readAll();
    return reply.status(204).send();
  });

  // Alias to preserve possible Flutter endpoint naming differences.
  app.post("/notifications/mark-all-read", { preHandler: [requireAuth] }, async (_req, reply) => {
    await notificationsService.readAll();
    return reply.status(204).send();
  });
}
