from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid
from datetime import datetime

class Sale(Base):
    __tablename__ = "sales"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, ForeignKey("customers.id"), nullable=True)
    shop_id = Column(String, ForeignKey("shops.id"), nullable=False)
    total_amount = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=True)
    payment_status = Column(String, default="paid")  # "paid", "unpaid", "partial"
    amount_paid = Column(Float, default=0.0)
    is_voided = Column(Boolean, default=False)
    void_reason = Column(String, nullable=True)

    # Relationships
    shop = relationship("Shop", back_populates="sales")
    session = relationship("Session", back_populates="sales")
    customer = relationship("Customer", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale")

class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    shop_id = Column(String, ForeignKey("shops.id"), nullable=False)
    sale_id = Column(String, ForeignKey("sales.id"))
    product_id = Column(String, ForeignKey("products.id"))
    quantity = Column(Float)
    unit_price = Column(Float)
    total_price = Column(Float)
    cost_price = Column(Float)

    # Relationships
    shop = relationship("Shop", back_populates="sale_items")
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")
    