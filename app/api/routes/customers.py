from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.customer import Customer
from app.db.models.sale import Sale
from pydantic import BaseModel
from typing import Optional
from app.api.dependencies import get_current_shop_id

router = APIRouter(prefix="/customers", tags=["Customers"])

class CustomerCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class CustomerOut(BaseModel):
    id: str
    name: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    total_credit: float
    created_at: str

    class Config:
        from_attributes = True

@router.post("/", response_model=CustomerOut)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)):
    new_customer = Customer(**customer.dict(), shop_id=shop_id)
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

@router.get("/", response_model=list[CustomerOut])
def get_customers(db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)):
    return db.query(Customer).filter(Customer.shop_id == shop_id).order_by(Customer.name).all()

@router.get("/debtors")
def get_debtors(db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)):
    """Return customers with outstanding credit (>0)."""
    debtors = db.query(Customer).filter(Customer.total_credit > 0, Customer.shop_id == shop_id).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "phone": c.phone,
            "total_credit": c.total_credit
        }
        for c in debtors
    ]

@router.post("/{customer_id}/record-payment")
def record_payment(customer_id: str, amount: float, db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)):
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.shop_id == shop_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    # Reduce total credit
    customer.total_credit = max(0, customer.total_credit - amount)
    db.commit()
    return {"message": f"Payment of {amount} recorded. Remaining credit: {customer.total_credit}"}