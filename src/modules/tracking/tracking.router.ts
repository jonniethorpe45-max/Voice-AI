import type { FastifyInstance } from "fastify";
import { z } from "zod";

import { prisma } from "../../db/client";
import { requireAuth } from "../../shared/middleware/auth";

const idParams = z.object({ id: z.string().uuid() });

function toTrackingRow(row: {
  id: string;
  leadId: string;
  event: string;
  description: string | null;
  timestamp: Date;
}) {
  return {
    id: row.id,
    lead_id: row.leadId,
    event: row.event,
    timestamp: row.timestamp.toISOString(),
    description: row.description,
  };
}

export async function trackingRouter(app: FastifyInstance): Promise<void> {
  app.get("/mail-tracking", { preHandler: [requireAuth] }, async (_request, reply) => {
    const rows = await prisma.mailEvent.findMany({
      orderBy: { timestamp: "desc" },
      take: 200,
    });
    return reply.send(rows.map(toTrackingRow));
  });

  app.get("/mail-tracking/:id", { preHandler: [requireAuth] }, async (request, reply) => {
    const { id } = idParams.parse(request.params);
    const row = await prisma.mailEvent.findUnique({ where: { id } });
    if (!row) return reply.status(404).send({ error: "Tracking event not found" });
    return reply.send(toTrackingRow(row));
  });

  app.get("/tracking", { preHandler: [requireAuth] }, async (_request, reply) => {
    const rows = await prisma.mailEvent.findMany({
      orderBy: { timestamp: "desc" },
      take: 200,
    });
    return reply.send(rows.map(toTrackingRow));
  });

  app.get("/tracking/:id", { preHandler: [requireAuth] }, async (request, reply) => {
    const { id } = idParams.parse(request.params);
    const row = await prisma.mailEvent.findUnique({ where: { id } });
    if (!row) return reply.status(404).send({ error: "Tracking event not found" });
    return reply.send(toTrackingRow(row));
  });
}
