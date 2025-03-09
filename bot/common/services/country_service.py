from enum import Enum
from typing import Optional

from api.app.gastronomy.schemas import CountryListResponse

from ...config import APIMethods
from ..utils import make_request

country_prefix = "gastronomy/countries"


class CountryEndpoints(Enum):
    COUNTRY_GET_LIST = f"{country_prefix}/"
    COUNTRY_UPDATE = f"{country_prefix}/"
    COUNTRY_CREATE = f"{country_prefix}/"
    COUNTRY_DELETE = f"{country_prefix}/"


async def get_country_list() -> Optional[CountryListResponse]:

    response = await make_request(
        sub_url=CountryEndpoints.COUNTRY_GET_LIST.value,
        method=APIMethods.GET.value,
    )

    return CountryListResponse.model_validate(response.get("data"))
