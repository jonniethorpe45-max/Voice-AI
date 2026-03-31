import cron from "node-cron";

import { runAllIngestion } from "../modules/ingestion/ingestion.service";

export function startIngestionScheduler() {
  cron.schedule("0 6 * * 1", async () => {
    await runAllIngestion("CA");
  });

  cron.schedule("0 6 * * 1", async () => {
    await runAllIngestion("FL");
  });
}
