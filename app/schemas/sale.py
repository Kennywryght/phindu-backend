from pydantic import BaseModel
from typing import List, Optional

class SaleItemCreate(BaseModel):
    product_id: str
    quantity: float
    unit: Optional[str] = None

class SaleCreate(BaseModel):
    items: List[SaleItemCreate]

class SaleResponse(BaseModel):
    id: str
    total_amount: float

    class Config:
        from_attributes = True

class BulkSaleItem(BaseModel):
    id: str          # <-- changed from UUID to str
    qty: float

class BulkSaleCreate(BaseModel):
    items: List[BulkSaleItem]