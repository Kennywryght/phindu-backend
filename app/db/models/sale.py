from sqlalchemy import Column, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid
from datetime import datetime

class Sale(Base):
    __tablename__ = "sales"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    total_amount = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=True)

    # Relationship (optional but helpful)
    session = relationship("Session", back_populates="sales")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sale_id = Column(String, ForeignKey("sales.id"))
    product_id = Column(String, ForeignKey("products.id"))
    quantity = Column(Float)
    unit_price = Column(Float)
    total_price = Column(Float)
    cost_price = Column(Float)

    product = relationship("Product")