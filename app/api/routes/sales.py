"""Sales API routes."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models.product import Product
from app.db.models.sale import Sale, SaleItem
from app.db.models.stock import StockBatch
from app.db.session import SessionLocal
from app.schemas.sale import SaleCreate, SaleResponse
from app.utils.conversion import to_kg

router = APIRouter(prefix="/sales", tags=["Sales"])


def get_db():
    """Yield a database session for route handlers."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=SaleResponse)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    """Create a new sale with items, updating product stock and tracking costs."""
    new_sale = Sale(id=str(uuid.uuid4()), total_amount=0)
    db.add(new_sale)

    total_amount = 0

    for item in sale.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # 🔥 HANDLE BULK PRODUCTS
        if product.type == "bulk":
            if not item.unit:
                raise HTTPException(status_code=400, detail="Unit required for bulk")

            qty_in_kg = to_kg(item.quantity, item.unit)

            if product.stock_qty < qty_in_kg:
                raise HTTPException(status_code=400, detail="Not enough stock")

            total_price = qty_in_kg * product.selling_price
            cost_price = (product.purchase_price or 0) * qty_in_kg

            product.stock_qty -= qty_in_kg

        # 🟢 HANDLE VARIANT PRODUCTS
        else:
            if product.stock_qty < item.quantity:
                raise HTTPException(status_code=400, detail="Not enough stock")

            total_price = item.quantity * product.selling_price
            cost_price = (product.purchase_price or 0) * item.quantity

            product.stock_qty -= item.quantity

            # 🔥 CHECK IF STOCK IS FINISHED
            if product.stock_qty <= 0:
                batch = db.query(StockBatch)\
                    .filter(StockBatch.product_id == product.id)\
                    .order_by(StockBatch.date_added.desc())\
                    .first()

                if batch and not batch.date_finished:
                    batch.date_finished = datetime.utcnow()

        total_amount += total_price

        sale_item = SaleItem(
            id=str(uuid.uuid4()),
            sale_id=new_sale.id,
            product_id=product.id,
            quantity=item.quantity,
            unit_price=product.selling_price,
            total_price=total_price,
            cost_price=cost_price
        )

        db.add(sale_item)

    new_sale.total_amount = total_amount

    db.commit()
    db.refresh(new_sale)

    return new_sale