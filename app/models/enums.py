from enum import Enum


class CountyKey(str, Enum):
    CA_LA = "CA_LA"
    CA_ORANGE = "CA_ORANGE"
    CA_EL_DORADO = "CA_EL_DORADO"
    CA_TULARE = "CA_TULARE"
    FL_LEE = "FL_LEE"
    FL_BREVARD = "FL_BREVARD"


class LeadStatus(str, Enum):
    NEW = "new"
    READY_FOR_REVIEW = "ready_for_review"
    PENDING_APPROVAL = "pending_approval"
    MAILED = "mailed"
    DELIVERED = "delivered"
    RETURNED = "returned"
    RESPONDED = "responded"


class LobVerificationStatus(str, Enum):
    NOT_STARTED = "not_started"
    VERIFIED = "verified"
    INVALID = "invalid"
    NEEDS_REVIEW = "needs_review"


class LetterTemplateKey(str, Enum):
    CALIFORNIA_OUTREACH = "california_outreach_letter"
    FLORIDA_OUTREACH = "florida_outreach_letter"


class LetterStatus(str, Enum):
    PREVIEW = "preview"
    APPROVED = "approved"
    REJECTED = "rejected"
    HOLD = "hold"
    SENT = "sent"


class TrackingStatus(str, Enum):
    SUBMITTED = "submitted"
    MAILED = "mailed"
    DELIVERED = "delivered"
    RETURNED = "returned"
    FAILED = "failed"


class ResponseChannel(str, Enum):
    EMAIL = "email"
    TWILIO = "twilio"
    MANUAL = "manual"
