from datetime import datetime
from sqlalchemy import func
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.session import Session
from app.db.models.sale import Sale
from app.db.models.expense import Expense
import uuid

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.post("/open")
def open_session(opening_balance: float = 0.0, db: Session = Depends(get_db)):
    # Check if there's already an active session
    active = db.query(Session).filter(Session.is_active == True).first()
    if active:
        raise HTTPException(status_code=400, detail="A session is already open")
    new_session = Session(
        id=str(uuid.uuid4()),
        opening_balance=opening_balance,
        is_active=True
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.post("/close")
def close_session(closing_balance: float, notes: str = None, db: Session = Depends(get_db)):
    active = db.query(Session).filter(Session.is_active == True).first()
    if not active:
        raise HTTPException(status_code=404, detail="No active session")
    # Calculate totals from linked sales and expenses
    sales_total = db.query(Sale).filter(Sale.session_id == active.id).with_entities(func.sum(Sale.total_amount)).scalar() or 0
    expenses_total = db.query(Expense).filter(Expense.session_id == active.id).with_entities(func.sum(Expense.amount)).scalar() or 0

    active.closed_at = datetime.utcnow()
    active.closing_balance = closing_balance
    active.total_sales = sales_total
    active.total_expenses = expenses_total
    active.is_active = False
    active.notes = notes
    db.commit()
    return {"message": "Session closed", "session": active}

@router.get("/current")
def get_current_session(db: Session = Depends(get_db)):
    active = db.query(Session).filter(Session.is_active == True).first()
    return active or {"detail": "No active session"}

@router.get("/")
def get_sessions(db: Session = Depends(get_db)):
    return db.query(Session).order_by(Session.opened_at.desc()).all()