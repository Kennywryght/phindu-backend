import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base
from sqlalchemy.orm import relationship

class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    shop_id = Column(String, ForeignKey("shops.id"), nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    total_credit = Column(Float, default=0.0)   # total amount owed
    created_at = Column(DateTime, server_default=func.now())
    shop = relationship("Shop", back_populates="customers")
    sales = relationship("Sale", back_populates="customer")