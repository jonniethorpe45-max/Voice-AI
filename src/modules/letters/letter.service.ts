import fs from "node:fs";
import path from "node:path";

import axios from "axios";
import Handlebars from "handlebars";
import type { Lead } from "@prisma/client";

import { env } from "../../config/env";

const templateSource = fs.readFileSync(path.join(process.cwd(), "src/modules/letters/templates/outreach_letter.html"), "utf-8");
const template = Handlebars.compile(templateSource);

function usd(value: number): string {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(value);
}

export function renderOutreachLetter(lead: Lead): string {
  return template({
    owner_name: lead.ownerName,
    mailing_address: lead.mailingAddress,
    city: lead.city,
    state: lead.state,
    zip: lead.zip,
    parcel_number: lead.parcelNumber,
    surplus_amount: usd(Number(lead.surplusAmount)),
    property_address: lead.propertyAddress,
    sale_date: lead.saleDate.toISOString().slice(0, 10),
    company_name: env.COMPANY_NAME,
    company_address: env.COMPANY_ADDRESS,
    response_phone: env.RESPONSE_PHONE,
    response_po_box: env.RESPONSE_PO_BOX,
    is_florida: lead.state === "FL",
    today_date: new Date().toISOString().slice(0, 10),
  });
}

export async function dispatchLobLetter(lead: Lead, html: string): Promise<{ id: string }> {
  if (!env.LOB_API_KEY || env.LOB_API_KEY.startsWith("test_")) {
    return { id: `local_${Date.now()}` };
  }

  const response = await axios.post(
    "https://api.lob.com/v1/letters",
    {
      to: { id: lead.lobAddressId },
      from: {
        name: env.LOB_RETURN_ADDRESS_NAME,
        address_line1: env.LOB_RETURN_ADDRESS_LINE1,
        address_city: env.LOB_RETURN_ADDRESS_CITY,
        address_state: env.LOB_RETURN_ADDRESS_STATE,
        address_zip: env.LOB_RETURN_ADDRESS_ZIP,
      },
      file: html,
      color: false,
      mail_type: "usps_first_class",
      double_sided: false,
    },
    {
      auth: { username: env.LOB_API_KEY, password: "" },
      timeout: 20000,
    },
  );

  return { id: String(response.data?.id ?? `lob_${Date.now()}`) };
}
