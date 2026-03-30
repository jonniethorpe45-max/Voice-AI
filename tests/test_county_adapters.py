from pathlib import Path

from app.models.enums import CountyKey
from app.services.ingestion.adapters import get_adapter


FIXTURE_MAP = {
    CountyKey.CA_LA: "ca_la.html",
    CountyKey.CA_ORANGE: "ca_orange.html",
    CountyKey.CA_EL_DORADO: "ca_el_dorado.html",
    CountyKey.CA_TULARE: "ca_tulare.html",
    CountyKey.FL_LEE: "fl_lee.html",
    CountyKey.FL_BREVARD: "fl_brevard.html",
}


def test_adapters_parse_records() -> None:
    fixtures_dir = Path(__file__).parent / "fixtures"
    for county_key, filename in FIXTURE_MAP.items():
        adapter = get_adapter(county_key.value)
        content = (fixtures_dir / filename).read_text(encoding="utf-8")
        records = adapter.parse(content, source_url="fixture://local")
        assert records, f"{county_key.value} should parse at least one record"
        rec = records[0]
        assert rec.owner_name
        assert rec.property_address
        assert rec.parcel_number
