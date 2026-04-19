import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base

class Shop(Base):
    __tablename__ = "shops"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    users = relationship("User", back_populates="shop")
    products = relationship("Product", back_populates="shop")
    sales = relationship("Sale", back_populates="shop")
    sale_items = relationship("SaleItem", back_populates="shop")
    expenses = relationship("Expense", back_populates="shop")
    customers = relationship("Customer", back_populates="shop")
    sessions = relationship("Session", back_populates="shop")
    sale_items = relationship("SaleItem", back_populates="shop")