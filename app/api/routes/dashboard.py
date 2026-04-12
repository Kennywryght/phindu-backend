from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.sale import SaleItem

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/")
def get_dashboard(db: Session = Depends(get_db)):
    items = db.query(SaleItem).all()
    total_revenue = 0
    total_cost = 0
    total_quantity = 0
    product_sales = {}

    for item in items:
        total_revenue += item.total_price
        total_cost += item.quantity * (item.cost_price or 0)
        total_quantity += item.quantity
        if item.product_id not in product_sales:
            product_sales[item.product_id] = 0
        product_sales[item.product_id] += item.quantity

    profit = total_revenue - total_cost
    top_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]
    best_product = max(product_sales, key=product_sales.get) if product_sales else None
    worst_product = min(product_sales, key=product_sales.get) if product_sales else None
    avg_sale_value = total_revenue / total_quantity if total_quantity else 0
    profit_margin = (profit / total_revenue * 100) if total_revenue else 0

    return {
        "total_revenue": total_revenue,
        "total_cost": total_cost,
        "profit": profit,
        "total_items_sold": total_quantity,
        "top_products": top_products,
        "best_product": best_product,
        "worst_product": worst_product,
        "avg_sale_value": avg_sale_value,
        "profit_margin": profit_margin
    }