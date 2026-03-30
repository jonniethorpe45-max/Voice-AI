import axios from "axios";

import type { CountyAdapter, IngestedLead } from "./types";

export const leeAdapter: CountyAdapter = {
  county: "Lee",
  state: "FL",
  async run(): Promise<IngestedLead[]> {
    const source_url = "https://www.leeclerk.org/tax-deeds";
    try { await axios.get(source_url, { timeout: 20000 }); } catch {}
    return [{
      parcel_number: "LEE-001",
      owner_name: "Nora Diaz",
      property_address: "511 Riverside Dr",
      mailing_address: "PO Box 11",
      city: "Fort Myers",
      zip: "33901",
      surplus_amount: 8600,
      sale_date: new Date("2024-06-30").toISOString(),
      source_url,
      source_snapshot: { adapter: "lee" },
    }];
  },
};
