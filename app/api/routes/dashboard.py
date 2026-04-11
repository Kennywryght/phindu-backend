"""Dashboard API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.sale import SaleItem

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_db():
    """Yield a database session for route handlers."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_dashboard(db: Session = Depends(get_db)):
    """Calculate and return dashboard metrics including revenue, costs, and top products."""
    items = db.query(SaleItem).all()

    total_revenue = 0
    total_cost = 0

    product_sales = {}

    for item in items:
        total_revenue += item.total_price
        total_cost += item.quantity * (item.cost_price or 0)

        # track product performance
        if item.product_id not in product_sales:
            product_sales[item.product_id] = 0

        product_sales[item.product_id] += item.quantity

    profit = total_revenue - total_cost

    # 🏆 top products
    top_products = sorted(
        product_sales.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]

    best_product = max(product_sales, key=product_sales.get) if product_sales else None
    worst_product = min(product_sales, key=product_sales.get) if product_sales else None

    return {
        "total_revenue": total_revenue,
        "total_cost": total_cost,
        "profit": profit,
        "top_products": top_products,
        "best_product": best_product,
        "worst_product": worst_product,
    }
