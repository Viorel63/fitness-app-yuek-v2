from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_premium = Column(Boolean, default=False)
    height = Column(Integer)
    weight = Column(Integer)
    age = Column(Integer)
    fitness_goal = Column(String(50))  # loss / mass / tone

    live_sessions = relationship("LiveSession", back_populates="user")
    workout_sessions = relationship("WorkoutSession", back_populates="user")
    created_programs = relationship("WorkoutProgram", back_populates="creator")
    friendships = relationship("Friendship", foreign_keys="Friendship.user_id", back_populates="user")


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500))
    type = Column(String(20))        # home / gym
    difficulty = Column(String(20))  # beginner / intermediate / advanced
    target_muscles = Column(String(200))

    live_sessions = relationship("LiveSession", back_populates="exercise")


class LiveSession(Base):
    __tablename__ = "live_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="live_sessions")
    exercise = relationship("Exercise", back_populates="live_sessions")


class WorkoutProgram(Base):
    __tablename__ = "workout_programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    difficulty = Column(String(20))
    duration_days = Column(Integer)
    created_by = Column(Integer, ForeignKey("users.id"))
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", back_populates="created_programs")
    sessions = relationship("WorkoutSession", back_populates="program")


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    program_id = Column(Integer, ForeignKey("workout_programs.id"), nullable=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)

    user = relationship("User", back_populates="workout_sessions")
    program = relationship("WorkoutProgram", back_populates="sessions")


class Friendship(Base):
    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    friend_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id], back_populates="friendships")
