"""
Запускать один раз для заполнения базы начальными упражнениями:
  python -m app.seed
"""
from .database import SessionLocal, engine
from . import models

models.Base.metadata.create_all(bind=engine)

EXERCISES = [
    # Дом
    {"name": "Приседания", "type": "home", "difficulty": "beginner", "target_muscles": "Ноги, ягодицы", "description": "Базовое упражнение для нижней части тела"},
    {"name": "Отжимания", "type": "home", "difficulty": "beginner", "target_muscles": "Грудь, трицепсы", "description": "Упражнение для груди и рук"},
    {"name": "Планка", "type": "home", "difficulty": "beginner", "target_muscles": "Кор, пресс", "description": "Статическое упражнение для кора"},
    {"name": "Выпады", "type": "home", "difficulty": "intermediate", "target_muscles": "Ноги, ягодицы", "description": "Упражнение для ног и баланса"},
    {"name": "Бёрпи", "type": "home", "difficulty": "advanced", "target_muscles": "Всё тело", "description": "Интенсивное кардио-упражнение"},
    # Зал
    {"name": "Жим лёжа", "type": "gym", "difficulty": "intermediate", "target_muscles": "Грудь, трицепсы, дельты", "description": "Базовое упражнение для груди"},
    {"name": "Становая тяга", "type": "gym", "difficulty": "advanced", "target_muscles": "Спина, ноги, кор", "description": "Одно из лучших базовых упражнений"},
    {"name": "Тяга верхнего блока", "type": "gym", "difficulty": "intermediate", "target_muscles": "Спина, бицепс", "description": "Упражнение для широчайших мышц"},
    {"name": "Жим гантелей сидя", "type": "gym", "difficulty": "intermediate", "target_muscles": "Дельты", "description": "Упражнение для плеч"},
    {"name": "Разгибания ног в тренажёре", "type": "gym", "difficulty": "beginner", "target_muscles": "Квадрицепсы", "description": "Изолирующее упражнение для квадрицепсов"},
]


def seed():
    db = SessionLocal()
    try:
        existing = db.query(models.Exercise).count()
        if existing > 0:
            print(f"⚠️  База уже содержит {existing} упражнений, пропускаем.")
            return

        for data in EXERCISES:
            db.add(models.Exercise(**data))
        db.commit()
        print(f"✅ Добавлено {len(EXERCISES)} упражнений.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
