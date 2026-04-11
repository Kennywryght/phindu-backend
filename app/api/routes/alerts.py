"""Alerts routes for inventory and stock notifications."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.product import Product

router = APIRouter(prefix="/alerts", tags=["Alerts"])

def get_db():
    """Yield a database session for request dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/low-stock")
def low_stock_alert(db: Session = Depends(get_db)):
    """Return products whose stock is at or below the low-stock threshold."""

    products = db.query(Product).filter(
        Product.stock_qty <= Product.low_stock_threshold,
        Product.is_deleted.is_(False)
    ).all()

    return products
