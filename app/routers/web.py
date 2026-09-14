from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from app import crud
from app.database import get_db
from app.schemas import AssetCreate, AssetStatus, AssetType, AssetUpdate, Environment

router = APIRouter(tags=["web"])


def form_context(request: Request, title: str, asset=None, error: str | None = None):
    return {"request": request, "title": title, "asset": asset, "error": error, "asset_types": AssetType, "environments": Environment, "statuses": AssetStatus}


def form_data(asset_tag: Annotated[str, Form()], name: Annotated[str, Form()], asset_type: Annotated[str, Form()], owner: Annotated[str, Form()], environment: Annotated[str, Form()], status_value: Annotated[str, Form(alias="status")], location: Annotated[str, Form()], operating_system: Annotated[str, Form()]) -> dict[str, str]:
    return {"asset_tag": asset_tag, "name": name, "asset_type": asset_type, "owner": owner, "environment": environment, "status": status_value, "location": location, "operating_system": operating_system}


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    return request.app.state.templates.TemplateResponse(request, "dashboard.html", {"counts": crud.dashboard_counts(db), "assets": crud.list_assets(db, limit=5)})


@router.get("/assets", response_class=HTMLResponse)
def assets_page(request: Request, search: str = "", environment: str = "", status_filter: str = "", db: Session = Depends(get_db)):
    context = {"assets": crud.list_assets(db, search or None, environment or None, status_filter or None), "search": search, "selected_environment": environment, "selected_status": status_filter, "environments": Environment, "statuses": AssetStatus}
    return request.app.state.templates.TemplateResponse(request, "assets.html", context)


@router.get("/assets/new", response_class=HTMLResponse)
def new_asset(request: Request):
    return request.app.state.templates.TemplateResponse(request, "asset_form.html", form_context(request, "Add Asset"))


@router.post("/assets/new")
def create_asset_page(request: Request, data: Annotated[dict[str, str], Depends(form_data)], db: Session = Depends(get_db)):
    try:
        crud.create_asset(db, AssetCreate(**data))
    except (ValidationError, IntegrityError) as exc:
        db.rollback()
        message = "Please correct all required fields." if isinstance(exc, ValidationError) else "That asset tag already exists."
        return request.app.state.templates.TemplateResponse(request, "asset_form.html", form_context(request, "Add Asset", data, message), status_code=422)
    return RedirectResponse("/assets", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/assets/{asset_id}/edit", response_class=HTMLResponse)
def edit_asset(request: Request, asset_id: int, db: Session = Depends(get_db)):
    asset = crud.get_asset(db, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return request.app.state.templates.TemplateResponse(request, "asset_form.html", form_context(request, "Edit Asset", asset))


@router.post("/assets/{asset_id}/edit")
def update_asset_page(request: Request, asset_id: int, data: Annotated[dict[str, str], Depends(form_data)], db: Session = Depends(get_db)):
    asset = crud.get_asset(db, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    try:
        crud.update_asset(db, asset, AssetUpdate(**data))
    except (ValidationError, IntegrityError) as exc:
        db.rollback()
        data["id"] = asset_id
        message = "Please correct all required fields." if isinstance(exc, ValidationError) else "That asset tag already exists."
        return request.app.state.templates.TemplateResponse(request, "asset_form.html", form_context(request, "Edit Asset", data, message), status_code=422)
    return RedirectResponse("/assets", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/assets/{asset_id}/delete")
def delete_asset_page(asset_id: int, db: Session = Depends(get_db)):
    asset = crud.get_asset(db, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    crud.delete_asset(db, asset)
    return RedirectResponse("/assets", status_code=status.HTTP_303_SEE_OTHER)
