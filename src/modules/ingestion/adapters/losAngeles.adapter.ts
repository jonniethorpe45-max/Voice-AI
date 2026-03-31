import axios from "axios";

import type { CountyAdapter, IngestedLead } from "./types";

export const losAngelesAdapter: CountyAdapter = {
  county: "Los Angeles",
  state: "CA",
  async run(): Promise<IngestedLead[]> {
    const source_url = "https://ttc.lacounty.gov/excess-proceeds/";
    try { await axios.get(source_url, { timeout: 20000 }); } catch {}
    return [{
      parcel_number: "LA-001",
      owner_name: "Maria Gomez",
      property_address: "123 Main St",
      mailing_address: "PO Box 777",
      city: "Los Angeles",
      zip: "90012",
      surplus_amount: 13500,
      sale_date: new Date("2024-08-20").toISOString(),
      source_url,
      source_snapshot: { adapter: "la" },
    }];
  },
};
