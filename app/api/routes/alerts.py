"""Alerts routes for inventory and stock notifications."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.product import Product
from app.api.dependencies import get_current_shop_id

router = APIRouter(prefix="/alerts", tags=["Alerts"])

def get_db():
    """Yield a database session for request dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/low-stock")
def low_stock_alert(db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)):
    """Return products whose stock is at or below the low-stock threshold."""

    products = db.query(Product).filter(
        Product.stock_qty <= Product.low_stock_threshold,
        Product.shop_id == shop_id,
        Product.is_deleted.is_(False),
    
    ).all()

    return products
