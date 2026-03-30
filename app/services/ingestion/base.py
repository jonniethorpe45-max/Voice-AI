from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any

from app.models.enums import CountyKey


@dataclass
class ParsedLeadRecord:
    state: str
    county_key: CountyKey
    county: str
    owner_name: str
    property_address: str | None
    mailing_address: str | None
    parcel_number: str | None
    sale_date: date | None
    surplus_amount: Decimal | None
    source_url: str
    source_hash: str
    manual_review_required: bool
    extraction_metadata: dict[str, Any]


class CountyAdapter:
    county_key: CountyKey
    county_name: str

    def parse(self, raw_content: str, source_url: str) -> list[ParsedLeadRecord]:
        raise NotImplementedError

