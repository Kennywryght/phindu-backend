from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from app.db.session import Base
import uuid
from datetime import datetime

class StockBatch(Base):
    __tablename__ = "stock_batches"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    product_id = Column(String, ForeignKey("products.id"))
    
    quantity_added = Column(Float)
    date_added = Column(DateTime, default=datetime.utcnow)
    date_finished = Column(DateTime, nullable=True)