from app.models.enums import CountyKey
from app.services.ingestion.adapters.common import StaticCountyAdapter


class CAOrangeAdapter(StaticCountyAdapter):
    county_key = CountyKey.CA_ORANGE

