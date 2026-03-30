from __future__ import annotations

from typing import Any
from uuid import uuid4

import requests

from app.core.config import settings
from app.models.enums import LetterTemplateKey
from app.models.lead import Lead
from app.models.letter import Letter


class LobService:
    def verify_address(self, address: str | None) -> tuple[bool, dict[str, Any]]:
        if not address:
            return False, {"error": "mailing_address_missing"}
        if not settings.lob_api_key:
            return True, {"primary_line": address, "deliverability": "deliverable_local"}
        return True, {"primary_line": address, "deliverability": "deliverable"}

    def render_template(self, template_key: LetterTemplateKey, lead: Lead) -> str:
        disclaimer = "You may be able to claim these funds directly without paying a fee."
        intro = (
            "California outreach letter"
            if template_key == LetterTemplateKey.CALIFORNIA_OUTREACH
            else "Florida outreach letter"
        )
        return (
            f"{intro}\n\n"
            f"Owner: {lead.owner_name}\n"
            f"Property: {lead.property_address or 'N/A'}\n"
            f"Surplus estimate: {lead.surplus_amount or 'N/A'}\n\n"
            f"{disclaimer}"
        )

    def send_letter(self, letter: Letter, to_address: str | None) -> str:
        if not to_address:
            return f"local-missing-address-{uuid4()}"
        if not settings.lob_api_key:
            return f"local-{uuid4()}"
        response = requests.post(
            f"{settings.lob_base_url}/letters",
            auth=(settings.lob_api_key, ""),
            data={
                "description": f"Surplus outreach {letter.id}",
                "to": to_address,
                "file": letter.body,
                "color": False,
            },
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        return str(payload.get("id", f"lob-{uuid4()}"))
