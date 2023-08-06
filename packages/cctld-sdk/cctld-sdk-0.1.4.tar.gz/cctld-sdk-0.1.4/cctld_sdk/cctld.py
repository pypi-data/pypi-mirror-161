from cctld_sdk.api import (
    RegistrarApiMixin,
    ContactApiMixin,
    DomainApiMixin,
    NsApiMixin,
    Client,
)
from .common.types import Singleton
from typing import Any


class CCTLD(
    Client,
    RegistrarApiMixin,
    ContactApiMixin,
    DomainApiMixin,
    NsApiMixin,
    metaclass=Singleton,
):
    pass
