from sqlalchemy import Column, String, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import uuid

class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    opened_at = Column(DateTime, server_default=func.now())
    closed_at = Column(DateTime, nullable=True)
    opening_balance = Column(Float, default=0.0)
    closing_balance = Column(Float, nullable=True)
    total_sales = Column(Float, default=0.0)
    total_expenses = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    notes = Column(String, nullable=True)

    sales = relationship("Sale", back_populates="session")