from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from app.db.session import Base
import uuid
from datetime import datetime

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, ForeignKey("products.id"))

    old_price = Column(Float)
    new_price = Column(Float)

    changed_at = Column(DateTime, default=datetime.utcnow)