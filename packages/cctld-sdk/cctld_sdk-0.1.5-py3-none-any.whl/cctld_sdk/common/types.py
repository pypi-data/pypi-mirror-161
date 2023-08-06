from enum import Enum
from typing import Any


class CCTLDActions(Enum):
    AUTH = "auth"
    # Contact Operations
    CONTACT_ADD = "cadd"
    CONTACT_LIST = "clist"
    CONTACT_EDIT = "cedit"
    CONTACT_DETAIL = "cidlist"
    CONTACT_DELETE = "cdel"
    CONTACT_LIST_IDS = "clistoid"
    # NS Operations
    NS_ADD = "nsadd"
    NS_LIST = "nslist"
    NS_DETAIL = "nsidlist"
    NS_LIST_IDS = "nsgetidlist"
    NS_LIST_NAMES = "nsnamelist"
    NS_LIST_IPS = "nsiplist"
    # Domain Operations
    DOMAIN_LIST = "dlist"
    DOMAIN_DETAIL = "didlist"
    DOMAIN_DETAIL_BY_DOMAIN_NAME = "dnamelist"
    DOMAIN_ADD = "dadd"
    DOMAIN_EDIT = "dedit"
    DOMAIN_DELEG_LIST = "ddeleglist"
    DOMAIN_DELEG = "ddeleg"
    DOMAIN_ACTIVATION = "activation"
    DOMAIN_STATUS = "dstatus"
    DOMAIN_DELETE = "ddel"
    WHOIS = "whois"
    # DOMAIN_EXTEND_EXPIRE_TIME = "chexpired"

    # User Options
    USER_PASSWORD_CHANGE = "changepass"
    USER_ALL_EVENT_LOGS = "reglog"
    USER_DOMAIN_EDIT_LOGS = "aclog"
    USER_BALANCE = "balance"


class Regions(Enum):
    KARAKALPAKSTAN = 1
    ANDIJAN_REGION = 2
    BUKHARA_REGION = 3
    JIZZAKH_REGION = 4
    KASHKADARYA_REGION = 5
    NAVOI_REGION = 6
    NAMANGAN_REGION = 7
    SAMARKAND_REGION = 8
    SURKHANDARYA_REGION = 9
    SIRDARYA_REGION = 10
    TASHKENT_REGION = 11
    FERGANA_REGION = 12
    KHOREZM_REGION = 13
    TASHKENT_CITY = 14


class Singleton(type):
    _instances = {}

    def __call__(cls, *args: Any, **kwds: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwds)
        return cls._instances[cls]
