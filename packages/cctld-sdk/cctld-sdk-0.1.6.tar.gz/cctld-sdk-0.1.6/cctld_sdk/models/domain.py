from dataclasses import dataclass


@dataclass
class Domain:
    name: str
    sCustID: int
    sAdminID: int
    sTechID: int
    sBillID: int
    pnsID: int
    snsID: int
    tnsID: str = ""
    qnsID: str = ""
    sDesc: str = ""
    lWhois: int = 0
