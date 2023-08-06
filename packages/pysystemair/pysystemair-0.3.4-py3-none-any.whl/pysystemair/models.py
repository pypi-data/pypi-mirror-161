from pydantic import BaseModel
from typing import Optional
from functools import partial
from .const import REG_TYPE

from box import Box

class Callbacks(BaseModel):
    holding_reg: partial
    input_reg: partial
    write_reg: partial

    class Config:
        arbitrary_types_allowed = True

class Register(BaseModel):
    addr: int
    value: Optional[float]=None
    reg_type: REG_TYPE

class InputRegister(Register):
    reg_type: REG_TYPE = REG_TYPE.INPUT


class HoldingRegister(Register):
    reg_type: REG_TYPE = REG_TYPE.HOLDING

## https://shop.systemair.com/upload/assets/SAVE_MODBUS_VARIABLE_LIST_20190116__REV__29_.PDF
## registry values - 1 for some reason




