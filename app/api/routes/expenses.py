from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.expense import Expense
from app.db.models.session import Session as SessionModel  # <-- Added import
import uuid
from app.api.dependencies import get_current_shop_id

router = APIRouter(prefix="/expenses", tags=["Expenses"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", operation_id="create_expense")
def create_expense(name: str, amount: float, category: str, db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)):
    expense = Expense(
        id=str(uuid.uuid4()),
        name=name,
        amount=amount,
        category=category,
    )
    db.add(expense)
    db.commit()

    return {"message": "Expense added"}
@router.get("/")

def get_expenses(db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)):
    return db.query(Expense).order_by(Expense.created_at.desc()).filter(Expense.shop_id == shop_id).all()

@router.post("/bulk", operation_id="create_bulk_expenses")
def create_expense(name: str, amount: float, category: str, db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)):
    active_session = db.query(SessionModel).filter(SessionModel.is_active == True).first()
    expense = Expense(
        id=str(uuid.uuid4()),
        name=name,
        amount=amount,
        category=category,
        session_id=active_session.id if active_session else None,
        shop_id=shop_id
    )
    db.add(expense)
    db.commit()
    return {"message": "Expense added"}