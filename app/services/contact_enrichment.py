from dataclasses import dataclass


@dataclass
class ContactEnrichmentResult:
    mailing_address_ok: bool
    phone: str | None = None
    email: str | None = None
    details: dict | None = None


class ContactEnrichmentService:
    def enrich(self, mailing_address: str | None) -> ContactEnrichmentResult:
        return ContactEnrichmentResult(
            mailing_address_ok=bool(mailing_address and mailing_address.strip()),
            details={"provider": "noop"},
        )
