from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel, EmailStr
from ..database import get_db
from ..auth import hash_password, verify_password, create_access_token
from ..config import ACCESS_TOKEN_EXPIRE_MINUTES
from .. import models

router = APIRouter(prefix="/auth", tags=["Auth"])


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    height: int = None
    weight: int = None
    age: int = None
    fitness_goal: str = None  # loss / mass / tone


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/register", status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(400, "Email уже занят")
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(400, "Имя пользователя уже занято")

    new_user = models.User(
        email=user.email,
        username=user.username,
        password_hash=hash_password(user.password),
        height=user.height,
        weight=user.weight,
        age=user.age,
        fitness_goal=user.fitness_goal,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Пользователь создан", "user_id": new_user.id}


@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверный email или пароль")

    token = create_access_token(
        data={"sub": db_user.email, "user_id": db_user.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}
