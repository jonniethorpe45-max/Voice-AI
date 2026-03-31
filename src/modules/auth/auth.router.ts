import type { FastifyInstance } from "fastify";

import { requireAuth } from "../../shared/middleware/auth";
import { loginBodySchema, refreshBodySchema } from "./auth.schema";
import { authService } from "./auth.service";

export async function authRouter(app: FastifyInstance): Promise<void> {
  app.post("/auth/login", async (request, reply) => {
    const body = loginBodySchema.parse(request.body);
    return reply.send(await authService.login(body.email, body.password));
  });

  app.post("/auth/logout", { preHandler: [requireAuth] }, async (request, reply) => {
    const body = refreshBodySchema.safeParse(request.body ?? {});
    // Flutter client sends empty body for logout; backend should still 204.
    if (body.success && body.data.refresh_token) {
      await authService.logout(body.data.refresh_token);
    }
    return reply.status(204).send();
  });

  app.post("/auth/refresh", async (request, reply) => {
    const body = refreshBodySchema.parse(request.body);
    return reply.send(await authService.refresh(body.refresh_token));
  });
}
