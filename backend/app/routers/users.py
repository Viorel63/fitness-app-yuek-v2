from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from ..database import get_db
from ..auth import get_current_user
from .. import models

router = APIRouter(prefix="/users", tags=["Users"])


class ProfileUpdate(BaseModel):
    username: Optional[str] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    age: Optional[int] = None
    fitness_goal: Optional[str] = None


@router.get("/me")
def get_me(current_user: models.User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "height": current_user.height,
        "weight": current_user.weight,
        "age": current_user.age,
        "fitness_goal": current_user.fitness_goal,
        "is_premium": current_user.is_premium,
        "joined_at": current_user.created_at,
    }


@router.patch("/me")
def update_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if data.username and data.username != current_user.username:
        if db.query(models.User).filter(models.User.username == data.username).first():
            raise HTTPException(400, "Имя пользователя уже занято")
        current_user.username = data.username
    if data.height is not None:
        current_user.height = data.height
    if data.weight is not None:
        current_user.weight = data.weight
    if data.age is not None:
        current_user.age = data.age
    if data.fitness_goal is not None:
        current_user.fitness_goal = data.fitness_goal

    db.commit()
    db.refresh(current_user)
    return {"message": "Профиль обновлён"}


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    return {
        "id": user.id,
        "username": user.username,
        "fitness_goal": user.fitness_goal,
        "is_premium": user.is_premium,
        "joined_at": user.created_at,
    }


@router.post("/{friend_id}/add-friend")
def add_friend(
    friend_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if friend_id == current_user.id:
        raise HTTPException(400, "Нельзя добавить себя в друзья")
    friend = db.query(models.User).filter(models.User.id == friend_id).first()
    if not friend:
        raise HTTPException(404, "Пользователь не найден")
    existing = db.query(models.Friendship).filter_by(
        user_id=current_user.id, friend_id=friend_id
    ).first()
    if existing:
        raise HTTPException(400, "Уже в друзьях")
    db.add(models.Friendship(user_id=current_user.id, friend_id=friend_id))
    db.commit()
    return {"message": f"{friend.username} добавлен в друзья"}


@router.get("/me/feed")
def friends_feed(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Лента активности друзей — последние тренировки"""
    friendships = db.query(models.Friendship).filter_by(user_id=current_user.id).all()
    friend_ids = [f.friend_id for f in friendships]

    sessions = (
        db.query(models.WorkoutSession)
        .filter(models.WorkoutSession.user_id.in_(friend_ids))
        .order_by(models.WorkoutSession.start_time.desc())
        .limit(20)
        .all()
    )

    result = []
    for s in sessions:
        result.append({
            "user_id": s.user_id,
            "username": s.user.username,
            "program": s.program.name if s.program else "Свободная тренировка",
            "started_at": s.start_time,
            "completed": s.completed,
        })
    return result
