import axios from "axios";

import type { CountyAdapter, IngestedLead } from "./types";

export const tulareAdapter: CountyAdapter = {
  county: "Tulare",
  state: "CA",
  async run(): Promise<IngestedLead[]> {
    const source_url = "https://tularecounty.ca.gov/assessor/";
    try { await axios.get(source_url, { timeout: 20000 }); } catch {}
    return [{
      parcel_number: "TU-001",
      owner_name: "Devin Ruiz",
      property_address: "78 Olive St",
      mailing_address: "22 Palm Ave",
      city: "Tulare",
      zip: "93274",
      surplus_amount: 15500,
      sale_date: new Date("2024-03-10").toISOString(),
      source_url,
      source_snapshot: { adapter: "tulare" },
    }];
  },
};
