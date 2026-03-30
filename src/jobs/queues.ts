import { Queue } from "bullmq";
import IORedis from "ioredis";

import { env } from "../config/env";

export const redis = new IORedis(env.REDIS_URL, { maxRetriesPerRequest: null });

export const addressVerificationQueue = new Queue("address-verification", { connection: redis });
export const letterDispatchQueue = new Queue("letter-dispatch", { connection: redis });
