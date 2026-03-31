import { cleanEnv, num, port, str } from "envalid";
import dotenv from "dotenv";

dotenv.config();

export const env = cleanEnv(process.env, {
  NODE_ENV: str({ choices: ["development", "test", "production"], default: "development" }),
  PORT: port({ default: 3000 }),
  API_VERSION: str({ default: "v1" }),

  DATABASE_URL: str(),
  REDIS_URL: str(),

  JWT_SECRET: str(),
  JWT_EXPIRES_IN: str({ default: "8h" }),
  REFRESH_TOKEN_EXPIRES_DAYS: num({ default: 30 }),

  LOB_API_KEY: str({ default: "" }),
  LOB_WEBHOOK_SECRET: str({ default: "" }),
  LOB_RETURN_ADDRESS_NAME: str(),
  LOB_RETURN_ADDRESS_LINE1: str(),
  LOB_RETURN_ADDRESS_CITY: str(),
  LOB_RETURN_ADDRESS_STATE: str(),
  LOB_RETURN_ADDRESS_ZIP: str(),

  RESPONSE_PHONE: str(),
  RESPONSE_PO_BOX: str(),
  COMPANY_NAME: str(),
  COMPANY_ADDRESS: str(),

  RATE_LIMIT_MAX: num({ default: 100 }),
  RATE_LIMIT_WINDOW_MS: num({ default: 60000 }),
});
