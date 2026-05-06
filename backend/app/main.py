from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routers import auth, users, exercises, workouts

# Создаём таблицы
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Fitness App API",
    description="Backend для фитнес-приложения",
    version="2.0.0",
)

# CORS — нужен для мобилки и браузера
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(exercises.router)
app.include_router(workouts.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "Fitness App API v2.0", "docs": "/docs"}


@app.get("/health", tags=["Root"])
def health():
    return {"status": "OK"}
