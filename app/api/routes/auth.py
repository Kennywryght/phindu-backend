from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.shop import Shop
from app.core.security import (
    verify_password,
    create_access_token,
    get_password_hash,
    decode_token
)
from pydantic import BaseModel
from typing import Optional
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class Token(BaseModel):
    access_token: str
    token_type: str

class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    shop_id: str

class RegisterRequest(BaseModel):
    shop_name: str
    full_name: str
    email: str
    password: str

# ------------------------------------------------------------------
# Dependency: get current user from token
# ------------------------------------------------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# ------------------------------------------------------------------
# Dependency: get current shop ID (depends on current user)
# ------------------------------------------------------------------
def get_current_shop_id(current_user: User = Depends(get_current_user)) -> str:
    return current_user.shop_id

# ------------------------------------------------------------------
# Auth endpoints
# ------------------------------------------------------------------
@router.post("/register", response_model=Token)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if len(data.password.encode('utf-8'))> 72:
        raise HTTPException(status_code=400, detail="Password too long (max 72 bytes)")
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    shop = Shop(id=str(uuid.uuid4()), name=data.shop_name)
    db.add(shop)
    db.flush()

    user = User(
        id=str(uuid.uuid4()),
        shop_id=shop.id,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        role="owner"
    )
    db.add(user)
    db.commit()

    token = create_access_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user