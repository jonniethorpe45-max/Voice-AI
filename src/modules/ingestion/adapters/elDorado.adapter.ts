import axios from "axios";

import type { CountyAdapter, IngestedLead } from "./types";

export const elDoradoAdapter: CountyAdapter = {
  county: "El Dorado",
  state: "CA",
  async run(): Promise<IngestedLead[]> {
    const source_url = "https://www.edcgov.us/Government/TTC/Pages/Tax_Sales.aspx";
    try { await axios.get(source_url, { timeout: 20000 }); } catch {}
    return [{
      parcel_number: "ED-001",
      owner_name: "Nora Allen",
      property_address: "1201 Sierra Way",
      mailing_address: "PO Box 120",
      city: "Placerville",
      zip: "95667",
      surplus_amount: 19400,
      sale_date: new Date("2024-05-01").toISOString(),
      source_url,
      source_snapshot: { adapter: "eldorado" },
    }];
  },
};
