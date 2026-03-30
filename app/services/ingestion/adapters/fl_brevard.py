from app.models.enums import CountyKey
from app.services.ingestion.adapters.common import StaticCountyAdapter


class FLBrevardAdapter(StaticCountyAdapter):
    county_key = CountyKey.FL_BREVARD
