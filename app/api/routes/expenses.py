from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.expense import Expense
import uuid

router = APIRouter(prefix="/expenses", tags=["Expenses"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_expense(name: str, amount: float, category: str, db: Session = Depends(get_db)):
    expense = Expense(
        id=str(uuid.uuid4()),
        name=name,
        amount=amount,
        category=category
    )
    db.add(expense)
    db.commit()

    return {"message": "Expense added"}
@router.get("/")

def get_expenses(db: Session = Depends(get_db)):
    return db.query(Expense).order_by(Expense.created_at.desc()).all()