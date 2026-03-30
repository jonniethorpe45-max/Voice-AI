from app.models.enums import CountyKey
from app.services.ingestion.adapters.ca_el_dorado import CAElDoradoAdapter
from app.services.ingestion.adapters.ca_la import CALosAngelesAdapter
from app.services.ingestion.adapters.ca_orange import CAOrangeAdapter
from app.services.ingestion.adapters.ca_tulare import CATulareAdapter
from app.services.ingestion.adapters.fl_brevard import FLBrevardAdapter
from app.services.ingestion.adapters.fl_lee import FLLeeAdapter

_ADAPTERS = {
    CountyKey.CA_LA.value: CALosAngelesAdapter(),
    CountyKey.CA_ORANGE.value: CAOrangeAdapter(),
    CountyKey.CA_EL_DORADO.value: CAElDoradoAdapter(),
    CountyKey.CA_TULARE.value: CATulareAdapter(),
    CountyKey.FL_LEE.value: FLLeeAdapter(),
    CountyKey.FL_BREVARD.value: FLBrevardAdapter(),
}


def get_adapter(county_key: str):
    if county_key not in _ADAPTERS:
        raise KeyError(f"Unsupported county adapter: {county_key}")
    return _ADAPTERS[county_key]
