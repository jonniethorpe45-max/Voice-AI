from app.models.enums import CountyKey
from app.services.ingestion.adapters.common import StaticCountyAdapter


class CAElDoradoAdapter(StaticCountyAdapter):
    county_key = CountyKey.CA_EL_DORADO
    county_name = "El Dorado"
