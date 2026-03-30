from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal
from html import unescape

from app.models.enums import CountyKey
from app.services.ingestion.base import ParsedLeadRecord
from app.services.normalization import source_hash


OWNER_PATTERNS = [
    r"<td>\s*Owner\s*</td>\s*<td>(.*?)</td>",
    r"<td>\s*Owner:\s*</td>\s*<td>(.*?)</td>",
    r'<span class="owner">(.*?)</span>',
    r"Owner Name:\s*(.*)",
]
PROPERTY_PATTERNS = [
    r"<td>\s*Property\s*</td>\s*<td>(.*?)</td>",
    r"<td>\s*Property Address:\s*</td>\s*<td>(.*?)</td>",
    r'<span class="property">(.*?)</span>',
    r"Property Address:\s*(.*)",
]
MAILING_PATTERNS = [
    r"<td>\s*Mailing\s*</td>\s*<td>(.*?)</td>",
    r"<td>\s*Mailing Address:\s*</td>\s*<td>(.*?)</td>",
    r'<span class="mailing">(.*?)</span>',
    r"Mailing Address:\s*(.*)",
]
PARCEL_PATTERNS = [
    r"<td>\s*APN\s*</td>\s*<td>(.*?)</td>",
    r"<td>\s*Parcel/APN:\s*</td>\s*<td>(.*?)</td>",
    r'<span class="apn">(.*?)</span>',
    r"APN:\s*(.*)",
    r"Parcel/APN:\s*(.*)",
]
SALE_DATE_PATTERNS = [
    r"<td>\s*Sale Date\s*</td>\s*<td>(.*?)</td>",
    r'<span class="sale_date">(.*?)</span>',
    r"Sale Date:\s*(.*)",
]
SURPLUS_PATTERNS = [
    r"<td>\s*Surplus\s*</td>\s*<td>(.*?)</td>",
    r"<td>\s*Surplus Amount:\s*</td>\s*<td>(.*?)</td>",
    r'<span class="surplus">(.*?)</span>',
    r"Surplus Amount:\s*(.*)",
]


def _clean(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = re.sub(r"<[^>]+>", " ", unescape(value))
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or None


def _extract_first(patterns: list[str], content: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, content, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return _clean(match.group(1))
    return None


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    return None


def _parse_amount(value: str | None) -> Decimal | None:
    if not value:
        return None
    cleaned = value.replace("$", "").replace(",", "").strip()
    try:
        return Decimal(cleaned)
    except Exception:
        return None


def parse_single_record(county_key: CountyKey, county_name: str, content: str, source_url: str) -> ParsedLeadRecord:
    # Handle simple one-row table fixtures with header row.
    row_cells = re.findall(r"<tr>\s*(.*?)\s*</tr>", content, flags=re.IGNORECASE | re.DOTALL)
    if len(row_cells) >= 2:
        headers = [_clean(x) or "" for x in re.findall(r"<th>(.*?)</th>", row_cells[0], flags=re.IGNORECASE | re.DOTALL)]
        values = [_clean(x) or "" for x in re.findall(r"<td>(.*?)</td>", row_cells[1], flags=re.IGNORECASE | re.DOTALL)]
        if headers and values and len(headers) == len(values):
            data = {h.lower(): v for h, v in zip(headers, values)}
            owner = data.get("owner", "UNKNOWN")
            property_address = data.get("property")
            mailing_address = data.get("mailing")
            parcel_number = data.get("parcel") or data.get("apn")
            sale_date_raw = data.get("sale date")
            surplus_raw = data.get("surplus") or data.get("surplus amount")
        else:
            owner = _extract_first(OWNER_PATTERNS, content) or "UNKNOWN"
            property_address = _extract_first(PROPERTY_PATTERNS, content)
            mailing_address = _extract_first(MAILING_PATTERNS, content)
            parcel_number = _extract_first(PARCEL_PATTERNS, content)
            sale_date_raw = _extract_first(SALE_DATE_PATTERNS, content)
            surplus_raw = _extract_first(SURPLUS_PATTERNS, content)
    else:
        owner = _extract_first(OWNER_PATTERNS, content) or "UNKNOWN"
        property_address = _extract_first(PROPERTY_PATTERNS, content)
        mailing_address = _extract_first(MAILING_PATTERNS, content)
        parcel_number = _extract_first(PARCEL_PATTERNS, content)
        sale_date_raw = _extract_first(SALE_DATE_PATTERNS, content)
        surplus_raw = _extract_first(SURPLUS_PATTERNS, content)
    state = "FL" if county_key.value.startswith("FL_") else "CA"
    manual_review_required = not bool(owner and property_address and parcel_number)
    return ParsedLeadRecord(
        state=state,
        county_key=county_key,
        county=county_name,
        owner_name=owner,
        property_address=property_address,
        mailing_address=mailing_address,
        parcel_number=parcel_number,
        sale_date=_parse_date(sale_date_raw),
        surplus_amount=_parse_amount(surplus_raw),
        source_url=source_url,
        source_hash=source_hash(county_key.value, owner, property_address or "", parcel_number or "", source_url),
        manual_review_required=manual_review_required,
        extraction_metadata={
            "adapter": county_key.value.lower(),
            "sale_date_raw": sale_date_raw,
            "surplus_raw": surplus_raw,
        },
    )


class StaticCountyAdapter:
    county_key: CountyKey
    county_name: str | None = None

    def parse(self, raw_content: str, source_url: str = "fixture://local") -> list[ParsedLeadRecord]:
        county_name = self.county_name or self.county_key.value.replace("CA_", "").replace("FL_", "").replace("_", " ").title()
        return [parse_single_record(self.county_key, county_name, raw_content, source_url)]
