import uuid
from sqlalchemy import Column, String, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    shop_id = Column(String, ForeignKey("shops.id"), nullable=False)
    opened_at = Column(DateTime, server_default=func.now())
    closed_at = Column(DateTime, nullable=True)
    opening_balance = Column(Float, default=0.0)
    closing_balance = Column(Float, nullable=True)
    total_sales = Column(Float, default=0.0)
    total_expenses = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    notes = Column(String, nullable=True)

    # Relationships
    shop = relationship("Shop", back_populates="sessions")
    sales = relationship("Sale", back_populates="session")