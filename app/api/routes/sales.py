"""Sales API routes."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models.product import Product
from app.db.models.sale import Sale, SaleItem
from app.db.models.stock import StockBatch
from app.db.models.session import Session as SessionModel  # <-- Added import
from app.db.session import get_db
from app.schemas.sale import SaleCreate, SaleResponse, BulkSaleCreate
from app.utils.conversion import to_kg
from app.api.dependencies import get_current_shop_id

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.post("/", response_model=SaleResponse)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)):
    """Create a new sale with items, update stock, and calculate totals."""

    new_sale = Sale(id=str(uuid.uuid4()), total_amount=0, shop_id=shop_id)  # <-- Set shop_id for the sale

    # Get active session and link if present
    active_session = db.query(SessionModel).filter(SessionModel.is_active == True, SessionModel.shop_id == shop_id).first()
    if active_session:
        new_sale.session_id = active_session.id

    db.add(new_sale)

    total_amount = 0

    for item in sale.items:
        product = db.query(Product).filter(Product.id == item.product_id, Product.shop_id == shop_id).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product.type == "bulk":
            if not item.unit:
                raise HTTPException(status_code=400, detail="Unit required for bulk")

            qty_in_kg = to_kg(item.quantity, item.unit)

            if product.stock_qty < qty_in_kg:
                raise HTTPException(status_code=400, detail="Not enough stock")

            total_price = qty_in_kg * product.selling_price
            cost_price = (product.purchase_price or 0) * qty_in_kg
            product.stock_qty -= qty_in_kg

        else:
            if product.stock_qty < item.quantity:
                raise HTTPException(status_code=400, detail="Not enough stock")

            total_price = item.quantity * product.selling_price
            cost_price = (product.purchase_price or 0) * item.quantity
            product.stock_qty -= item.quantity

            if product.stock_qty <= 0:
                batch = (
                    db.query(StockBatch)
                    .filter(StockBatch.product_id == product.id, StockBatch.shop_id == shop_id)
                    .order_by(StockBatch.date_added.desc())
                    .first()
                )
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


@router.post("/bulk")
def bulk_sales(data: BulkSaleCreate, db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)):
    """Quick bulk sales for POS (no detailed breakdown)."""
    active_session = db.query(SessionModel).filter(SessionModel.is_active == True, SessionModel.shop_id == shop_id).first()

    for item in data.items:
        product = db.query(Product).filter(Product.id == item.id, Product.shop_id == shop_id).first()
        if not product:
            continue
        if product.stock_qty < item.qty:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product.name}")

        sale = Sale(
            
            id=str(uuid.uuid4()),
            total_amount=product.selling_price * item.qty,
            session_id=active_session.id if active_session else None,  # <-- Set session_id
            shop_id=shop_id  # <-- Set shop_id for the sale
        )
        db.add(sale)
        product.stock_qty -= item.qty

    db.commit()
    return {"message": "Bulk sale recorded"}


@router.get("/")
def get_sales(db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)):
    sales = db.query(Sale).filter(Sale.shop_id == shop_id).order_by(Sale.created_at.desc()).all()
    result = []
    for sale in sales:
        items = db.query(SaleItem).filter(SaleItem.sale_id == sale.id).all()
        product_names = []
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product_names.append(product.name)
        result.append({
            "id": sale.id,
            "total_amount": sale.total_amount,
            "created_at": sale.created_at,
            "products": product_names
        })
    return result

@router.post("/{sale_id}/void")
def void_sale(sale_id: str, reason: str = None, db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)):
    sale = db.query(Sale).filter(Sale.id == sale_id, Sale.shop_id == shop_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    if sale.is_voided:
        raise HTTPException(status_code=400, detail="Sale already voided")

    # Restore stock for each item
    items = db.query(SaleItem).filter(SaleItem.sale_id == sale_id, SaleItem.shop_id == shop_id).all()
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id, Product.shop_id == shop_id).first()
        if product:
            if product.type == "bulk":
                # For bulk products, quantity was already converted to kg
                product.stock_qty += item.quantity
            else:
                product.stock_qty += item.quantity

    sale.is_voided = True
    sale.void_reason = reason
    db.commit()
    return {"message": "Sale voided successfully"}