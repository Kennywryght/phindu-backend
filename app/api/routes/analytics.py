from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.stock import StockBatch
from app.db.session import get_db
from app.db.models.product import Product
from app.db.models.sale import Sale

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/sell-speed")
def get_sell_speed(db: Session = Depends(get_db)):
    batches = db.query(StockBatch).all()

    results = []

    for batch in batches:
        if batch.date_finished:
            days = (batch.date_finished - batch.date_added).days

            results.append({
                "product_id": batch.product_id,
                "quantity": batch.quantity_added,
                "days_to_sell": days
            })

    return results

@router.get("/insights")
def insights(db: Session = Depends(get_db)):

    total_products = db.query(Product).count()
    total_sales = db.query(Sale).count()

    return {
        "message": "Insights ready",
        "total_products": total_products,
        "total_sales": total_sales
    }