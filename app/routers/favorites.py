"""Rotas de favoritos."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import GUEST_USER
from app.database import get_db
from app.models import Favorite, Property
from app.schemas import FavoriteToggle

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


@router.post("", response_model=dict)
def toggle_favorite(payload: FavoriteToggle, db: Session = Depends(get_db)):
    """
    Alterna o status de favorito de um imóvel.

    Body:
    {
        "property_id": 1,
        "is_favorite": true
    }

    Resposta: status atualizado do imóvel nos favoritos.
    """
    property_exists = db.get(Property, payload.property_id) is not None
    if not property_exists:
        raise HTTPException(
            status_code=404,
            detail=f"Imóvel com ID {payload.property_id} não encontrado.",
        )

    favorite = (
        db.query(Favorite)
        .filter(
            Favorite.property_id == payload.property_id,
            Favorite.user_id == GUEST_USER,
        )
        .first()
    )

    if payload.is_favorite:
        if favorite is None:
            db.add(
                Favorite(property_id=payload.property_id, user_id=GUEST_USER)
            )
    else:
        if favorite is not None:
            db.delete(favorite)

    db.commit()

    return {
        "property_id": payload.property_id,
        "is_favorite": payload.is_favorite,
        "message": "Imóvel adicionado aos favoritos."
        if payload.is_favorite
        else "Imóvel removido dos favoritos.",
    }
