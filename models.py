from enum import Enum

from database import Base

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime


class UserStatus(str, Enum):
    alive = 'alive'
    dead = 'dead'
    finished = 'finished'


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    status: Mapped[UserStatus] = mapped_column(server_default=UserStatus.alive)
    status_updated_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    first_message: Mapped[datetime] = mapped_column(nullable=True)
    second_message: Mapped[datetime] = mapped_column(nullable=True)
    third_message: Mapped[datetime] = mapped_column(nullable=True)
