from cctld_sdk.common.types import Regions

from dataclasses import dataclass, field
import inspect


@dataclass
class Person:
    sID: str = field(init=False, default=None)
    id: str = field(init=False, default=None)
    sNameEN: str
    sPhone: str
    sFax: str = field(init=False, default=None, repr=False)
    sEMail: str
    sPost: int = field(init=False, default=None, repr=False)
    sType: str = field(init=False, default="l", repr=False)
    sIduzUrl: str = field(init=False, default=None, repr=False)
    sNick: str = field(init=False, default=None, repr=False)
    sContract: str = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        self.sNameRU = self.sNameUZ = self.sNameEN
        if self.id:
            self.sID = self.id


@dataclass
class Address:
    sAddressEN: str
    sCityEN: str
    sRegion: int = field(init=False, default=Regions.TASHKENT_CITY.value)
    sCountryEN: str = field(init=False, default="UZ", repr=False)
    sState: str

    def __post_init__(self) -> None:
        self.sAddressRU = self.sAddressUZ = self.sAddressEN
        self.sCityRU = self.sCityUZ = self.sCityEN
        self.sCountryRU = self.sCountryUZ = self.sCountryEN


@dataclass
class Passport:
    sPassportCode: str
    sPassport: int
    sPassportWhoEN: str

    sPassportYear: int
    sPassportMonth: int
    sPassportDay: int

    def __post_init__(self) -> None:
        self.sPassportWhoRU = self.sPassportWhoUZ = self.sPassportWhoEN


@dataclass
class Business:
    sOrgEN: str
    sBankNameEN: str
    sRS: int
    sINN: int
    sMFO: int
    sOKONH: int

    def __post_init__(self) -> None:
        self.sOrgRU = self.sOrgUZ = self.sOrgEN
        self.sBankNameRU = self.sBankNameUZ = self.sBankNameEN


@dataclass
class PhysicalContact(Person, Passport, Address):
    def __post_init__(self) -> None:
        Person.__post_init__(self)
        Passport.__post_init__(self)
        Address.__post_init__(self)

    @classmethod
    def from_dict(cls, env):
        return cls(
            **{k: v for k, v in env.items() if k in inspect.signature(cls).parameters}
        )


@dataclass
class LegalContact(PhysicalContact, Business):
    def __post_init__(self) -> None:
        PhysicalContact.__post_init__(self)
        Business.__post_init__(self)
