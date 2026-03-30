import type { ActivityLog, Lead, MailEvent } from "@prisma/client";
import { dbLeadStatusToApi, dbLobVerificationToApi } from "./statusMappings";

export type LeadWithRelations = Lead & { mailEvents?: MailEvent[]; activityLogs?: ActivityLog[] };

function asNumber(value: unknown): number {
  if (typeof value === "number") return value;
  if (typeof value === "string") return Number(value);
  if (value && typeof value === "object" && "toString" in value) {
    return Number((value as { toString(): string }).toString());
  }
  return 0;
}

export function serializeLead(lead: LeadWithRelations) {
  return {
    id: lead.id,
    parcel_number: lead.parcelNumber,
    owner_name: lead.ownerName,
    owner_phone: lead.ownerPhone,
    owner_email: lead.ownerEmail,
    property_address: lead.propertyAddress,
    mailing_address: lead.mailingAddress,
    city: lead.city,
    county: lead.county,
    state: lead.state,
    zip: lead.zip,
    surplus_amount: asNumber(lead.surplusAmount),
    sale_date: lead.saleDate.toISOString(),
    status: dbLeadStatusToApi(lead.status),
    lob_verification_status: dbLobVerificationToApi(lead.lobVerificationStatus),
    lob_address_id: lead.lobAddressId,
    lob_letter_id: lead.lobLetterId,
    manual_review_required: lead.manualReviewRequired,
    legal_review_cleared: lead.legalReviewCleared,
    flagged_for_legal_review: lead.flaggedForLegalReview,
    assignment_confidence: lead.assignmentConfidence,
    data_source: lead.dataSource,
    source_url: lead.sourceUrl,
    notes: lead.notes,
    created_at: lead.createdAt.toISOString(),
    updated_at: lead.updatedAt.toISOString(),
    mail_events: (lead.mailEvents ?? []).map((x) => ({
      event: x.event as "submitted" | "mailed" | "delivered" | "returned" | "in_transit",
      timestamp: x.timestamp.toISOString(),
      description: x.description,
    })),
    activity_log: (lead.activityLogs ?? []).map((x) => ({
      action: x.action,
      operator_name: x.operatorName,
      note: x.note,
      timestamp: x.timestamp.toISOString(),
    })),
  };
}
