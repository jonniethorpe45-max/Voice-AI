import { LeadStatus, LobVerificationStatus, NotificationEventType, Role } from "@prisma/client";

export const dbLeadStatusToApiMap: Record<LeadStatus, string> = {
  IMPORTED: "imported",
  ADDRESS_VERIFIED: "addressVerified",
  LETTER_GENERATED: "letterGenerated",
  PENDING_APPROVAL: "pendingApproval",
  ON_HOLD: "onHold",
  APPROVED: "approved",
  SENT: "sent",
  DELIVERED: "delivered",
  RETURNED: "returned",
  FAILED: "failed",
};

export const apiLeadStatusToDbMap: Record<string, LeadStatus> = {
  imported: "IMPORTED",
  addressVerified: "ADDRESS_VERIFIED",
  letterGenerated: "LETTER_GENERATED",
  pendingApproval: "PENDING_APPROVAL",
  onHold: "ON_HOLD",
  approved: "APPROVED",
  sent: "SENT",
  delivered: "DELIVERED",
  returned: "RETURNED",
  failed: "FAILED",
};

export const dbLobVerificationToApiMap: Record<LobVerificationStatus, string> = {
  NOT_STARTED: "notStarted",
  PENDING: "pending",
  VERIFIED: "verified",
  CORRECTED: "corrected",
  UNDELIVERABLE: "undeliverable",
  FAILED: "failed",
};

export const dbNotificationTypeToApiMap: Record<NotificationEventType, string> = {
  NEW_LEAD_READY: "newLeadReady",
  LETTER_RETURNED: "letterReturned",
  RECIPIENT_RESPONDED: "recipientResponded",
  LEGAL_REVIEW_REQUIRED: "legalReviewRequired",
  APPROVAL_COMPLETED: "approvalCompleted",
};

export function dbLeadStatusToApi(status: LeadStatus): string {
  return dbLeadStatusToApiMap[status];
}

export function apiLeadStatusToDb(status?: string | null): LeadStatus | undefined {
  if (!status) return undefined;
  return apiLeadStatusToDbMap[status];
}

export function dbLobVerificationToApi(status: LobVerificationStatus): string {
  return dbLobVerificationToApiMap[status];
}

export function dbNotificationTypeToApi(type: NotificationEventType): string {
  return dbNotificationTypeToApiMap[type];
}

export function toApiRole(role: Role): "admin" | "reviewer" {
  return role === "ADMIN" ? "admin" : "reviewer";
}
