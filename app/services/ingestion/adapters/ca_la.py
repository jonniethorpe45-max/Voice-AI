from app.models.enums import CountyKey
from app.services.ingestion.adapters.common import StaticCountyAdapter


class CALosAngelesAdapter(StaticCountyAdapter):
    county_key = CountyKey.CA_LA
    county_name = "Los Angeles"
