"""Rotas de favoritos vinculadas ao usuário autenticado."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Favorite, Property, User
from app.schemas import FavoriteResult, FavoriteToggle, PropertyOut
from app.serializers import property_to_dict

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


@router.get("", response_model=List[PropertyOut])
def list_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista somente os imóveis favoritados pelo usuário da sessão."""
    rows = (
        db.query(Property)
        .join(Favorite, Favorite.property_id == Property.id)
        .filter(
            Favorite.user_id == current_user.id,
            Property.is_active.is_(True),
        )
        .order_by(Favorite.created_at.desc())
        .all()
    )
    return [property_to_dict(prop, is_favorite=True) for prop in rows]


@router.post("", response_model=FavoriteResult)
def toggle_favorite(
    payload: FavoriteToggle,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Adiciona ou remove um favorito da conta autenticada."""
    prop = db.get(Property, payload.property_id)
    if prop is None or not prop.is_active:
        raise HTTPException(
            status_code=404,
            detail=f"Imóvel com ID {payload.property_id} não encontrado.",
        )

    favorite = (
        db.query(Favorite)
        .filter(
            Favorite.property_id == payload.property_id,
            Favorite.user_id == current_user.id,
        )
        .first()
    )

    if payload.is_favorite and favorite is None:
        db.add(
            Favorite(property_id=payload.property_id, user_id=current_user.id)
        )
    elif not payload.is_favorite and favorite is not None:
        db.delete(favorite)

    db.commit()
    return {
        "property_id": payload.property_id,
        "is_favorite": payload.is_favorite,
        "message": "Imóvel adicionado aos favoritos."
        if payload.is_favorite
        else "Imóvel removido dos favoritos.",
    }


@router.delete("/{property_id}", response_model=FavoriteResult)
def remove_favorite(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove um favorito de forma idempotente."""
    favorite = (
        db.query(Favorite)
        .filter(
            Favorite.property_id == property_id,
            Favorite.user_id == current_user.id,
        )
        .first()
    )
    if favorite is not None:
        db.delete(favorite)
        db.commit()
    return {
        "property_id": property_id,
        "is_favorite": False,
        "message": "Imóvel removido dos favoritos.",
    }
