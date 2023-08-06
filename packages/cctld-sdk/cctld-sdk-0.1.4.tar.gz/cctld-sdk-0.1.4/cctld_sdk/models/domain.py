from dataclasses import dataclass
from typing import Optional


@dataclass
class Domain:
    name: str
    sCustID: int
    sAdminID: int
    sTechID: int
    sBillID: int
    pnsID: int
    snsID: int
    tnsID: Optional[str] = ""
    qnsID: Optional[str] = ""
    sDesc: Optional[str] = ""
    lWhois: int = 0
