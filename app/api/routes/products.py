"""Product API routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models.product import Product
from app.db.models.price_history import PriceHistory
from app.db.models.sale import SaleItem
from app.db.models.stock import StockBatch
from app.db.session import SessionLocal
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.api.dependencies import get_current_shop_id

router = APIRouter(prefix="/products", tags=["Products"])


def get_db():
    """Yield a database session for route handlers."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ProductOut)
def create_product(product: ProductCreate,
                   db: Session = Depends(get_db), 
                   shop_id: str = Depends(get_current_shop_id)):
    new_product = Product(
        shop_id=shop_id,
        name=product.name,
        category=product.category,
        type=product.type,
        unit=product.unit,
        selling_price=product.selling_price,
        purchase_price=product.purchase_price,
        stock_qty=product.stock_qty,
        parent_id=product.parent_id
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    batch = StockBatch(
        product_id=new_product.id,
        quantity_added=new_product.stock_qty,
        date_added=datetime.utcnow()
    )
    db.add(batch)
    db.commit()

    return new_product


@router.get("/", response_model=list[ProductOut])
def get_products(
    include_deleted: bool = False,
    db: Session = Depends(get_db),
    shop_id: str = Depends(get_current_shop_id)
    ):
    query = db.query(Product).filter(Product.shop_id == shop_id)
    if not include_deleted:
        query = query.filter(Product.is_deleted == False)
    return query.all()



@router.delete("/{product_id}")
def delete_product(product_id: str, db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)):
    """Delete a product, soft delete if it has sales, hard delete otherwise."""
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    sale_exists = db.query(SaleItem).filter(SaleItem.product_id == product_id).first()

    if sale_exists:
        product.is_deleted = True
        db.commit()
        return {"message": "Product soft-deleted (used in sales)"}

    db.delete(product)
    db.commit()
    return {"message": "Product permanently deleted"}


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: str,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    shop_id: str = Depends(get_current_shop_id)
):
    """Update product fields and handle stock changes."""
    product = db.query(Product).filter(Product.id == product_id, Product.shop_id == shop_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product_update.dict(exclude_unset=True)

    if "selling_price" in update_data:
        history = PriceHistory(
            product_id=product.id,
            old_price=product.selling_price,
            new_price=update_data["selling_price"]
        )
        db.add(history)

    if "stock_qty" in update_data:
        new_stock = update_data["stock_qty"]
        if new_stock > product.stock_qty:
            added_qty = new_stock - product.stock_qty
            batch = StockBatch(
                product_id=product.id,
                quantity_added=added_qty,
                date_added=datetime.utcnow()
            )
            db.add(batch)
        product.stock_qty = new_stock

    for field, value in update_data.items():
        if field != "stock_qty":
            setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


@router.put("/restore/{product_id}")
def restore_product(product_id: str, db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)):
    """Restore a soft-deleted product."""
    product = db.query(Product).filter(Product.id == product_id, Product.shop_id == shop_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_deleted = False
    db.commit()
    return {"message": "Product restored"}


@router.put("/archive/{product_id}")
def archive_product(product_id: str, db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)):
    """Archive a product so it is hidden from normal listings."""
    product = db.query(Product).filter(Product.id == product_id, Product.shop_id == shop_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.archived = True
    db.commit()
    return {"message": "Product archived"}


@router.put("/unarchive/{product_id}")
def unarchive_product(product_id: str, db: Session = Depends(get_db), shop_id: str = Depends(get_current_shop_id)):
    product = db.query(Product).filter(Product.id == product_id, Product.shop_id == shop_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.archived = False
    db.commit()
    return {"message": "Product unarchived"}