from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.db.session import get_db
from app.db.models.stock import StockBatch
from app.db.models.product import Product
from app.db.models.sale import Sale

router = APIRouter(prefix="/analytics", tags=["Analytics"])


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


@router.get("/revenue-trend")
def revenue_trend(db: Session = Depends(get_db)):
    """Return total revenue for each of the last 6 days."""
    today = datetime.utcnow().date()
    six_days_ago = today - timedelta(days=5)
    
    results = []
    for i in range(6):
        day = six_days_ago + timedelta(days=i)
        next_day = day + timedelta(days=1)
        
        total = db.query(func.sum(Sale.total_amount)).filter(
            Sale.created_at >= day,
            Sale.created_at < next_day
        ).scalar() or 0
        
        results.append({
            "date": day.isoformat(),
            "revenue": float(total)
        })
    
    return results