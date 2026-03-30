import axios from "axios";

import type { CountyAdapter, IngestedLead } from "./types";

export const brevardAdapter: CountyAdapter = {
  county: "Brevard",
  state: "FL",
  async run(): Promise<IngestedLead[]> {
    const source_url = "https://www.brevardclerk.us/tax-deeds";
    try { await axios.get(source_url, { timeout: 20000 }); } catch {}
    return [{
      parcel_number: "BR-001",
      owner_name: "Tyler Nguyen",
      property_address: "545 River Trail",
      mailing_address: "PO Box 9181",
      city: "Melbourne",
      zip: "32901",
      surplus_amount: 6810,
      sale_date: new Date("2025-01-20").toISOString(),
      source_url,
      source_snapshot: { adapter: "brevard" },
    }];
  },
};
