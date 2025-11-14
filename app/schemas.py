from typing import Annotated, Optional, List
from annotated_types import Ge, Le
from pydantic import BaseModel, EmailStr, Field, StringConstraints, ConfigDict

NameStr = Annotated[str, StringConstraints(min_length = 1, max_length = 100)]
OrderNumberStr = Annotated[str, StringConstraints(min_length = 3, max_length = 20)]
customerSinceInt = Annotated[int, Ge(2000), Le(2100)]
total_centsInt = Annotated[int, Ge(1), Le(1000000)]

class CustomerCreate(BaseModel):
    name: NameStr
    email: EmailStr
    customer_since: customerSinceInt

class CustomerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: NameStr
    email: EmailStr
    customer_since: customerSinceInt

class CustomerUpdate(BaseModel):
    name: Optional[NameStr]=None
    email: Optional[EmailStr]=None
    customer_since: Optional[customerSinceInt]=None

class OrderCreate(BaseModel):
    order_number: OrderNumberStr
    total_cents: total_centsInt
    customer_id: Optional[int]=None

class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_number : OrderNumberStr
    total_cents : total_centsInt
    customer_id : int
