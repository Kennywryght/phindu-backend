from fastapi import Depends
from app.api.routes.auth import get_current_user
from app.db.models.user import User

def get_current_shop_id(current_user: User = Depends(get_current_user)) -> str:
    return current_user.shop_id

__all__ = ["get_current_shop_id"]