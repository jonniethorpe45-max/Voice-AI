import type { FastifyInstance } from "fastify";

import { requireAuth } from "../../shared/middleware/auth";
import { getDashboardStats } from "./dashboard.service";

export async function dashboardRouter(app: FastifyInstance): Promise<void> {
  app.get("/dashboard/stats", { preHandler: [requireAuth] }, async (_request, reply) => {
    return reply.send(await getDashboardStats());
  });
}
