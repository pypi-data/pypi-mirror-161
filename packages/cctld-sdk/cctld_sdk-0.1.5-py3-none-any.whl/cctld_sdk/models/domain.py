from dataclasses import dataclass, field
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
    tnsID: field(init=False, default="", repr=False)
    qnsID: field(init=False, default="", repr=False)
    sDesc: field(init=False, default="", repr=False)
    lWhois: int = 0
