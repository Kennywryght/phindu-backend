"""Product Pydantic schemas."""

from typing import Optional
from pydantic import BaseModel


class ProductCreate(BaseModel):
    """Schema for creating a new product."""
    name: str
    category: Optional[str] = None
    type: str  # "variant" or "bulk"
    unit: str  # "kg", "g", "piece"
    selling_price: float
    purchase_price: float
    stock_qty: float
    parent_id: Optional[str] = None


class ProductOut(BaseModel):
    """Schema for product output."""
    id: str
    name: str
    category: Optional[str]
    type: str
    unit: str
    selling_price: float
    purchase_price: float
    stock_qty: float
    archived: bool = False

    class Config:
        from_attributes = True


class ProductUpdate(BaseModel):
    """Schema for updating product fields."""
    name: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    unit: Optional[str] = None
    selling_price: Optional[float] = None
    purchase_price: Optional[float] = None
    stock_qty: Optional[float] = None