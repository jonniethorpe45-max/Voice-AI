export interface CountyAdapter {
  county: string;
  state: "CA" | "FL";
  run(): Promise<IngestedLead[]>;
}

export interface IngestedLead {
  parcel_number: string;
  owner_name: string;
  property_address: string;
  mailing_address: string;
  city: string;
  zip: string;
  surplus_amount: number;
  sale_date: string;
  source_url: string;
  source_snapshot: Record<string, unknown>;
}
