from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Asset
from app.schemas import AssetCreate, AssetUpdate


def list_assets(db: Session, search: str | None = None, environment: str | None = None, status: str | None = None, limit: int | None = None) -> list[Asset]:
    query = select(Asset)
    if search:
        pattern = f"%{search.strip()}%"
        query = query.where(or_(Asset.asset_tag.ilike(pattern), Asset.name.ilike(pattern), Asset.owner.ilike(pattern), Asset.location.ilike(pattern)))
    if environment:
        query = query.where(Asset.environment == environment)
    if status:
        query = query.where(Asset.status == status)
    query = query.order_by(Asset.created_at.desc(), Asset.id.desc())
    if limit:
        query = query.limit(limit)
    return list(db.scalars(query).all())


def get_asset(db: Session, asset_id: int) -> Asset | None:
    return db.get(Asset, asset_id)


def create_asset(db: Session, data: AssetCreate) -> Asset:
    asset = Asset(**data.model_dump(mode="json"))
    db.add(asset); db.commit(); db.refresh(asset)
    return asset


def update_asset(db: Session, asset: Asset, data: AssetUpdate) -> Asset:
    for key, value in data.model_dump(mode="json").items():
        setattr(asset, key, value)
    asset.updated_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(asset)
    return asset


def delete_asset(db: Session, asset: Asset) -> None:
    db.delete(asset); db.commit()


def dashboard_counts(db: Session) -> dict[str, int]:
    return {
        "total": db.scalar(select(func.count()).select_from(Asset)) or 0,
        "production": db.scalar(select(func.count()).select_from(Asset).where(Asset.environment == "Production")) or 0,
        "active": db.scalar(select(func.count()).select_from(Asset).where(Asset.status == "Active")) or 0,
        "maintenance": db.scalar(select(func.count()).select_from(Asset).where(Asset.status == "Maintenance")) or 0,
    }
