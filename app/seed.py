from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User, UserRole


def seed_users(db: Session) -> None:
    existing = db.scalar(select(User.id).limit(1))
    if existing:
        return

    db.add_all(
        [
            User(name="Vikram Viewer", role=UserRole.VIEWER),
            User(name="Anika Analyst", role=UserRole.ANALYST),
            User(name="Arjun Admin", role=UserRole.ADMIN),
        ]
    )
    db.commit()
