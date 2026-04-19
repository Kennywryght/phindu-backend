from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Boolean
from app.db.session import Base
import uuid
from datetime import datetime
from sqlalchemy.orm import relationship

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    amount = Column(Float)
    category = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=True)
    shop = relationship("Shop", back_populates="expenses")
    shop_id = Column(String, ForeignKey("shops.id"), nullable=False) 