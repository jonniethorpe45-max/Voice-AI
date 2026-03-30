import { env } from "./env";

export const APP = {
  name: "Tax Deeds API",
  apiPrefix: `/${env.API_VERSION}`,
  port: env.PORT,
  dashboardCacheTtlSeconds: 60,
};
