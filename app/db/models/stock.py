from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid
from datetime import datetime

class StockBatch(Base):
    __tablename__ = "stock_batches"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    shop_id = Column(String, ForeignKey("shops.id"), nullable=False)   # <-- add this
    product_id = Column(String, ForeignKey("products.id"))
    quantity_added = Column(Float)
    date_added = Column(DateTime, default=datetime.utcnow)
    date_finished = Column(DateTime, nullable=True)

    # Relationships
    shop = relationship("Shop", back_populates="stock_batches")
    product = relationship("Product", back_populates="stock_batches")