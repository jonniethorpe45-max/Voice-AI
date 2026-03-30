from app.models.enums import CountyKey
from app.services.ingestion.adapters.common import StaticCountyAdapter


class CATulareAdapter(StaticCountyAdapter):
    county_key = CountyKey.CA_TULARE
    county_name = "Tulare"
