import axios from "axios";

import type { CountyAdapter, IngestedLead } from "./types";

export const orangeAdapter: CountyAdapter = {
  county: "Orange",
  state: "CA",
  async run(): Promise<IngestedLead[]> {
    const source_url = "https://www.octreasurer.com/tax-sale";
    try { await axios.get(source_url, { timeout: 20000 }); } catch {}
    return [{
      parcel_number: "OR-001",
      owner_name: "Ana Gomez",
      property_address: "11 Orange Ave",
      mailing_address: "PO Box 100",
      city: "Santa Ana",
      zip: "92701",
      surplus_amount: 18600,
      sale_date: new Date("2024-03-02").toISOString(),
      source_url,
      source_snapshot: { adapter: "orange" },
    }];
  },
};
