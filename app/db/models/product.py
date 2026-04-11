"""Product database model."""

import uuid

from sqlalchemy import Column, String, Float, ForeignKey, Boolean
from app.db.session import Base


class Product(Base):
    """Product model representing items for sale."""
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    name = Column(String, nullable=False)
    category = Column(String)

    type = Column(String)  # "variant" or "bulk"
    unit = Column(String)  # "kg", "g", "piece"

    selling_price = Column(Float)
    purchase_price = Column(Float)

    stock_qty = Column(Float, default=0)

    parent_id = Column(String, ForeignKey("products.id"), nullable=True)
    is_deleted = Column(Boolean, default=False)
    # is_archived = Column(Boolean, default=False)

    low_stock_threshold = Column(Float, default=5)
