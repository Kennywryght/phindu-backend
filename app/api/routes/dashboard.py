from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db.models.sale import Sale, SaleItem
from app.db.models.expense import Expense
from app.db.models.session import Session as SessionModel

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/")
def get_dashboard(
    session_id: str = Query(None),
    db: Session = Depends(get_db)
):
    # If no session_id provided, try to use the currently active session
    if not session_id:
        active_session = db.query(SessionModel).filter(SessionModel.is_active == True).first()
        if active_session:
            session_id = active_session.id

    # Base query for SaleItem – optionally filter by session
    sale_items_query = db.query(SaleItem).join(Sale)
    if session_id:
        sale_items_query = sale_items_query.filter(Sale.session_id == session_id)

    items = sale_items_query.all()

    total_revenue = 0.0
    total_cost = 0.0
    total_quantity = 0
    product_sales = {}

    for item in items:
        total_revenue += item.total_price
        total_cost += item.quantity * (item.cost_price or 0)
        total_quantity += item.quantity
        if item.product_id not in product_sales:
            product_sales[item.product_id] = 0
        product_sales[item.product_id] += item.quantity

    
    top_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]
    best_product = max(product_sales, key=product_sales.get) if product_sales else None
    worst_product = min(product_sales, key=product_sales.get) if product_sales else None
    avg_sale_value = total_revenue / total_quantity if total_quantity else 0.0
    profit_margin = (profit / total_revenue * 100) if total_revenue else 0.0

    # Total expenses – also filter by session
    expenses_query = db.query(func.sum(Expense.amount))
    if session_id:
        expenses_query = expenses_query.filter(Expense.session_id == session_id)
    total_expenses = expenses_query.scalar() or 0.0
    
    profit = total_revenue - total_cost-total_expenses

    return {
        "session_id": session_id,
        "total_revenue": total_revenue,
        "total_cost": total_cost,
        "profit": profit,
        "total_items_sold": total_quantity,
        "top_products": top_products,
        "best_product": best_product,
        "worst_product": worst_product,
        "avg_sale_value": avg_sale_value,
        "profit_margin": profit_margin,
        "total_expenses": total_expenses
    }