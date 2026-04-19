from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import extract

from app.db.session import get_db
from app.db.models.stock import StockBatch
from app.db.models.product import Product
from app.db.models.sale import Sale
from app.api.dependencies import get_current_shop_id
from app.db.models.sale import SaleItem

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/sell-speed")
def get_sell_speed(db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)):
    batches = db.query(StockBatch).filter(StockBatch.shop_id == shop_id).all()
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
def insights(db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)):
    total_products = db.query(Product).filter(Product.shop_id == shop_id).count()
    total_sales = db.query(Sale).filter(Sale.shop_id == shop_id).count()

    return {
        "message": "Insights ready",
        "total_products": total_products,
        "total_sales": total_sales
    }


@router.get("/revenue-trend")
def revenue_trend(db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)):
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

@router.get("/top-products")
def top_products(
    period: str = "day",  # "day", "week", "month"
    db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)
):
    """Return top 10 products by quantity sold in the given period."""
    now = datetime.utcnow()
    if period == "day":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start_date = now - timedelta(days=now.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "month":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start_date = now - timedelta(days=30)  # fallback

    # Query: sum quantity per product, join Sale for date filter
    results = (
        db.query(
            Product.id,
            Product.name,
            func.sum(SaleItem.quantity).label("total_quantity")
        )
        .join(SaleItem, SaleItem.product_id == Product.id)
        .join(Sale, Sale.id == SaleItem.sale_id)
        .filter(Sale.created_at >= start_date, Sale.created_at <= now)
        .group_by(Product.id, Product.name)
        .order_by(func.sum(SaleItem.quantity).desc())
        .limit(10)
        .all()
    )

    return [
        {
            "id": r.id,
            "name": r.name,
            "quantity": float(r.total_quantity or 0)
        }
        for r in results
    ]
    
@router.get("/profit-margins")
def profit_margins(db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)):
    """Return profit margin (profit / revenue) for each product based on all sales."""
    
    # Subquery to get total revenue and total cost per product
    results = (
        db.query(
            Product.id,
            Product.name,
            func.sum(SaleItem.total_price).label("revenue"),
            func.sum(SaleItem.quantity * SaleItem.cost_price).label("cost")
        )
        .join(SaleItem, SaleItem.product_id == Product.id)
        .join(Sale, Sale.id == SaleItem.sale_id)
        .filter(Sale.shop_id == shop_id)    
        .group_by(Product.id, Product.name)
        .all()
    )

    margins = []
    for r in results:
        revenue = float(r.revenue or 0)
        cost = float(r.cost or 0)
        profit = revenue - cost
        margin_percent = (profit / revenue * 100) if revenue > 0 else 0.0
        margins.append({
            "id": r.id,
            "name": r.name,
            "revenue": revenue,
            "cost": cost,
            "profit": profit,
            "margin_percent": round(margin_percent, 2)
        })

    # Sort by margin percent descending
    margins.sort(key=lambda x: x["margin_percent"], reverse=True)
    return margins
@router.get("/peak-hours")
def peak_hours(db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)):
    """Return sales count grouped by hour of day (0-23)."""
    results = (
        db.query(
            extract('hour', Sale.created_at).label('hour'),
            func.count(Sale.id).label('count')
        )
        .filter(Sale.shop_id == shop_id)
        .group_by('hour')
        .order_by('hour')
        .all()
    )

    hours = [0] * 24
    for r in results:
        hours[int(r.hour)] = r.count

    return {"hours": hours}

@router.get("/expense-breakdown")
def expense_breakdown(db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)):
    """Sum expenses grouped by category."""
    results = (
        db.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        )
        .filter(Expense.shop_id == shop_id)
        .group_by(Expense.category)
        .all()
    )

    return [
        {"category": r.category or "Uncategorized", "total": float(r.total)}
        for r in results
    ]