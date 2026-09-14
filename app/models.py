from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, Unicode
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_tag: Mapped[str] = mapped_column(Unicode(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(Unicode(150), nullable=False)
    asset_type: Mapped[str] = mapped_column(Unicode(30), nullable=False)
    owner: Mapped[str] = mapped_column(Unicode(100), nullable=False)
    environment: Mapped[str] = mapped_column(Unicode(30), nullable=False)
    status: Mapped[str] = mapped_column(Unicode(30), nullable=False)
    location: Mapped[str] = mapped_column(Unicode(150), nullable=False)
    operating_system: Mapped[str] = mapped_column(Unicode(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
