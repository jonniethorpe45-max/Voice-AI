import Fastify from "fastify";
import cors from "@fastify/cors";
import rateLimit from "@fastify/rate-limit";

import { APP } from "./src/config/app";
import { env } from "./src/config/env";
import { errorHandler } from "./src/shared/middleware/errorHandler";
import { authRouter } from "./src/modules/auth/auth.router";
import { leadsRouter } from "./src/modules/leads/leads.router";
import { dashboardRouter } from "./src/modules/dashboard/dashboard.router";
import { notificationsRouter } from "./src/modules/notifications/notifications.router";
import { lettersRouter } from "./src/modules/letters/letters.router";
import { ingestionRouter } from "./src/modules/ingestion/ingestion.service";
import { trackingRouter } from "./src/modules/tracking/tracking.router";
import { webhookRouter } from "./src/modules/mail-tracking/webhook.router";
import { startIngestionScheduler } from "./src/jobs/ingestionScheduler";

export function buildServer() {
  const app = Fastify({ logger: true });
  app.register(cors, { origin: true });
  app.register(rateLimit, { max: env.RATE_LIMIT_MAX, timeWindow: env.RATE_LIMIT_WINDOW_MS });
  app.setErrorHandler(errorHandler);
  app.get("/health", async () => ({ status: "ok" }));

  app.register(authRouter, { prefix: APP.apiPrefix });
  app.register(leadsRouter, { prefix: APP.apiPrefix });
  app.register(dashboardRouter, { prefix: APP.apiPrefix });
  app.register(notificationsRouter, { prefix: APP.apiPrefix });
  app.register(lettersRouter, { prefix: APP.apiPrefix });
  app.register(ingestionRouter, { prefix: APP.apiPrefix });
  app.register(trackingRouter, { prefix: APP.apiPrefix });
  app.register(webhookRouter, { prefix: APP.apiPrefix });
  return app;
}

if (process.argv[1] && process.argv[1].includes("server")) {
  const app = buildServer();
  Promise.all([
    import("./src/jobs/addressVerification.job"),
    import("./src/jobs/letterDispatch.job"),
  ])
    .then(async () => {
      startIngestionScheduler();
      await app.listen({ host: "0.0.0.0", port: APP.port });
    })
    .catch((err) => {
      app.log.error(err);
      process.exit(1);
    });
}
