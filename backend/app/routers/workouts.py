from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..database import get_db
from ..auth import get_current_user
from .. import models

router = APIRouter(prefix="/workouts", tags=["Workouts"])


# --- Schemas ---

class ProgramCreate(BaseModel):
    name: str
    description: Optional[str] = None
    difficulty: Optional[str] = None  # beginner / intermediate / advanced
    duration_days: Optional[int] = None
    is_public: bool = True


class SessionStart(BaseModel):
    program_id: Optional[int] = None  # None = свободная тренировка


# --- Programs ---

@router.get("/programs")
def list_programs(
    public_only: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.WorkoutProgram)
    if public_only:
        query = query.filter(models.WorkoutProgram.is_public == True)
    else:
        query = query.filter(
            (models.WorkoutProgram.created_by == current_user.id) |
            (models.WorkoutProgram.is_public == True)
        )
    programs = query.order_by(models.WorkoutProgram.created_at.desc()).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "difficulty": p.difficulty,
            "duration_days": p.duration_days,
            "is_public": p.is_public,
            "created_by": p.creator.username if p.creator else None,
        }
        for p in programs
    ]


@router.post("/programs", status_code=201)
def create_program(
    data: ProgramCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    program = models.WorkoutProgram(
        name=data.name,
        description=data.description,
        difficulty=data.difficulty,
        duration_days=data.duration_days,
        is_public=data.is_public,
        created_by=current_user.id,
    )
    db.add(program)
    db.commit()
    db.refresh(program)
    return {"message": "Программа создана", "program_id": program.id}


@router.get("/programs/{program_id}")
def get_program(program_id: int, db: Session = Depends(get_db)):
    p = db.query(models.WorkoutProgram).filter(models.WorkoutProgram.id == program_id).first()
    if not p:
        raise HTTPException(404, "Программа не найдена")
    return p


# --- Sessions ---

@router.post("/sessions/start")
def start_session(
    data: SessionStart,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Закрываем незавершённые сессии
    db.query(models.WorkoutSession).filter_by(
        user_id=current_user.id, completed=False
    ).update({"end_time": datetime.utcnow(), "completed": False})

    session = models.WorkoutSession(
        user_id=current_user.id,
        program_id=data.program_id,
        start_time=datetime.utcnow(),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"message": "Тренировка начата", "session_id": session.id}


@router.post("/sessions/{session_id}/finish")
def finish_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    session = db.query(models.WorkoutSession).filter_by(
        id=session_id, user_id=current_user.id
    ).first()
    if not session:
        raise HTTPException(404, "Сессия не найдена")
    if session.completed:
        raise HTTPException(400, "Тренировка уже завершена")

    session.end_time = datetime.utcnow()
    session.completed = True
    db.commit()

    duration = int((session.end_time - session.start_time).total_seconds() // 60)
    return {"message": "Тренировка завершена", "duration_minutes": duration}


@router.get("/sessions/history")
def get_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    sessions = (
        db.query(models.WorkoutSession)
        .filter_by(user_id=current_user.id)
        .order_by(models.WorkoutSession.start_time.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": s.id,
            "program": s.program.name if s.program else "Свободная тренировка",
            "start_time": s.start_time,
            "end_time": s.end_time,
            "completed": s.completed,
            "duration_minutes": (
                int((s.end_time - s.start_time).total_seconds() // 60)
                if s.end_time else None
            ),
        }
        for s in sessions
    ]
