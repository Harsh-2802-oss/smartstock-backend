from typing import List, Optional

from pydantic import BaseModel, Field


class RegisterIn(BaseModel):
    store_name: str = Field(min_length=2, max_length=100)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=72)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    user_id: int
    email: str
    store_id: int
    store_name: str


class ProductIn(BaseModel):
    product_name: str = Field(min_length=1, max_length=150)
    sku: str = Field(min_length=1, max_length=50)
    selling_price: float = Field(gt=0)
    cost_price: float = Field(ge=0, default=0)
    current_stock: int = Field(ge=0, default=0)
    reorder_threshold: int = Field(ge=0, default=5)
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None


class ProductPatch(BaseModel):
    supplier_id: Optional[int] = None
    reorder_threshold: Optional[int] = Field(default=None, ge=0)
    selling_price: Optional[float] = Field(default=None, gt=0)
    cost_price: Optional[float] = Field(default=None, ge=0)


class SaleLine(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=1000)


class SaleIn(BaseModel):
    items: List[SaleLine] = Field(min_length=1, max_length=50)
