from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud
from app.config import get_settings
from app.database import get_db
from app.schemas import AssetCreate, AssetRead, AssetUpdate

router = APIRouter(prefix="/api", tags=["assets"])


@router.get("/info", tags=["application"])
def application_info() -> dict[str, str]:
    settings = get_settings()
    return {"application": settings.app_name, "version": settings.app_version, "environment": settings.app_env}


@router.get("/assets", response_model=list[AssetRead])
def assets(search: str | None = None, environment: str | None = None, status_filter: str | None = None, db: Session = Depends(get_db)):
    return crud.list_assets(db, search, environment, status_filter)


@router.get("/assets/{asset_id}", response_model=AssetRead)
def asset(asset_id: int, db: Session = Depends(get_db)):
    result = crud.get_asset(db, asset_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return result


@router.post("/assets", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
def add_asset(data: AssetCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_asset(db, data)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Asset tag already exists") from exc


@router.put("/assets/{asset_id}", response_model=AssetRead)
def replace_asset(asset_id: int, data: AssetUpdate, db: Session = Depends(get_db)):
    existing = crud.get_asset(db, asset_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    try:
        return crud.update_asset(db, existing, data)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Asset tag already exists") from exc


@router.delete("/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_asset(asset_id: int, db: Session = Depends(get_db)) -> Response:
    existing = crud.get_asset(db, asset_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    crud.delete_asset(db, existing)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
