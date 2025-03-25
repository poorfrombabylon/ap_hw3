from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from datetime import datetime
from typing import Optional

from app.database import SessionLocal
from app.models import Link, User
from app.schemas import LinkCreate, LinkUpdate, LinkInfo
from app.utils import generate_short_code
from app.redis_client import redis_client
from app.routers.auth import get_current_user, optional_user
from sqlalchemy import or_

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/links/shorten", response_model=LinkInfo)
def create_short_link(
    link: LinkCreate,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(optional_user)
):
    short_code = generate_short_code()

    if link.custom_alias:
        existing = db.query(Link).filter_by(custom_alias=link.custom_alias).first()
        if existing:
            raise HTTPException(status_code=400, detail="Custom alias already taken")

    new_link = Link(
        short_code=short_code,
        custom_alias=link.custom_alias,
        original_url=link.original_url,
        user_id=user.id if user else None,
        expires_at=link.expires_at
    )
    db.add(new_link)
    db.commit()
    db.refresh(new_link)

    redis_client.set(short_code, link.original_url)

    return new_link

@router.get("/links/search", response_model=LinkInfo)
def search_link_by_original_url(
    original_url: str = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    link = db.query(Link).filter(
        Link.original_url == original_url,
        Link.user_id == user.id
    ).first()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    return link


@router.get("/{short_code}")
def redirect_link(short_code: str, db: Session = Depends(get_db)):
    original_url = redis_client.get(short_code)

    link = db.query(Link).filter_by(short_code=short_code).first()

    if not link:
        raise HTTPException(status_code=404, detail="Not found")

    if link.expires_at and datetime.utcnow() > link.expires_at:
        raise HTTPException(status_code=410, detail="Link expired")

    if not original_url:
        redis_client.set(short_code, link.original_url)

    link.click_count += 1
    link.last_accessed = datetime.utcnow()
    db.commit()

    return RedirectResponse(link.original_url)


@router.delete("/links/{short_code}")
def delete_link(short_code: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    link = db.query(Link).filter_by(short_code=short_code).first()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if link.user_id is None:
        raise HTTPException(status_code=403, detail="Anonymous link cannot be deleted")

    if link.user_id != user.id:
        raise HTTPException(status_code=403, detail="You do not own this link")

    db.delete(link)
    db.commit()
    redis_client.delete(short_code)

    return {"detail": "Deleted"}


@router.put("/links/{short_code}", response_model=LinkInfo)
def update_link(
    short_code: str,
    data: LinkUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    link = db.query(Link).filter_by(short_code=short_code).first()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if link.user_id is None:
        raise HTTPException(status_code=403, detail="Anonymous link cannot be modified")

    if link.user_id != user.id:
        raise HTTPException(status_code=403, detail="You do not own this link")

    link.original_url = data.original_url
    db.commit()
    redis_client.set(short_code, link.original_url)

    return link

@router.get("/links/{short_code}/stats", response_model=LinkInfo)
def link_stats(short_code: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    link = db.query(Link).filter_by(short_code=short_code).first()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if link.user_id != user.id:
        raise HTTPException(status_code=403)

    return link
