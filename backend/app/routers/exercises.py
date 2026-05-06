from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from .. import models

router = APIRouter(prefix="/exercises", tags=["Exercises"])


@router.get("/")
def get_exercises(
    type: Optional[str] = None,       # home / gym
    difficulty: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Exercise)
    if type:
        query = query.filter(models.Exercise.type == type)
    if difficulty:
        query = query.filter(models.Exercise.difficulty == difficulty)
    exercises = query.all()
    return exercises


@router.get("/{exercise_id}")
def get_exercise(exercise_id: int, db: Session = Depends(get_db)):
    ex = db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()
    if not ex:
        raise HTTPException(404, "Упражнение не найдено")
    return ex


@router.get("/{exercise_id}/live")
def get_live_count(exercise_id: int, db: Session = Depends(get_db)):
    ex = db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()
    if not ex:
        raise HTTPException(404, "Упражнение не найдено")
    count = db.query(models.LiveSession).filter_by(
        exercise_id=exercise_id, is_active=True
    ).count()
    return {
        "exercise_id": exercise_id,
        "exercise_name": ex.name,
        "active_users": count,
        "message": f"Сейчас делают {ex.name}: {count} человек",
    }
