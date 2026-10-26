"""Rotas de imóveis, filtros, edição, exclusão e estatísticas."""

from datetime import date
from typing import List, Literal, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_optional_user
from app.models import Favorite, Property, User
from app.schemas import (
    ActionResponse,
    MessageOut,
    PaginatedProperties,
    PropertyIn,
    PropertyOut,
    PropertyUpdate,
    StatsOut,
)
from app.serializers import property_to_dict

router = APIRouter(prefix="/api", tags=["properties"])
SortOption = Literal["price_asc", "price_desc", "area_desc", "recent"]


def _favorite_ids(db: Session, user: Optional[User]) -> set:
    if user is None:
        return set()
    return {
        row.property_id
        for row in db.query(Favorite.property_id).filter(
            Favorite.user_id == user.id
        )
    }


def _require_owned_property(
    db: Session, property_id: int, current_user: User
) -> Property:
    prop = db.get(Property, property_id)
    if prop is None or not prop.is_active:
        raise HTTPException(
            status_code=404, detail=f"Imóvel com ID {property_id} não encontrado."
        )
    if prop.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para alterar este imóvel.",
        )
    return prop


@router.get(
    "/properties",
    response_model=Union[List[PropertyOut], PaginatedProperties],
)
def get_properties(
    property_type: Optional[str] = Query(None),
    purpose: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    location: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None, min_length=2, max_length=2),
    bedrooms: Optional[int] = Query(None, ge=0),
    bathrooms: Optional[int] = Query(None, ge=0),
    min_area: Optional[float] = Query(None, ge=0),
    max_area: Optional[float] = Query(None, ge=0),
    featured: Optional[bool] = Query(None),
    query: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort: SortOption = Query("recent"),
    with_meta: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Lista imóveis ativos com filtros, ordenação e paginação opcional."""
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=400, detail="Preço mínimo maior que o máximo.")
    if min_area is not None and max_area is not None and min_area > max_area:
        raise HTTPException(status_code=400, detail="Área mínima maior que a máxima.")

    result = db.query(Property).filter(Property.is_active.is_(True))

    if property_type and property_type.lower() != "todos":
        result = result.filter(
            func.lower(Property.property_type) == property_type.lower()
        )
    if purpose and purpose.lower() != "todos":
        result = result.filter(func.lower(Property.purpose) == purpose.lower())
    if min_price is not None:
        result = result.filter(Property.price >= min_price)
    if max_price is not None:
        result = result.filter(Property.price <= max_price)
    if location and location.strip():
        pattern = f"%{location.strip()}%"
        result = result.filter(
            or_(
                Property.location.ilike(pattern),
                Property.neighborhood.ilike(pattern),
                Property.city.ilike(pattern),
            )
        )
    if city and city.strip():
        result = result.filter(Property.city.ilike(f"%{city.strip()}%"))
    if state and state.strip():
        result = result.filter(func.upper(Property.state) == state.strip().upper())
    if bedrooms is not None and bedrooms > 0:
        result = result.filter(Property.bedrooms >= bedrooms)
    if bathrooms is not None and bathrooms > 0:
        result = result.filter(Property.bathrooms >= bathrooms)
    if min_area is not None:
        result = result.filter(Property.area_sqm >= min_area)
    if max_area is not None:
        result = result.filter(Property.area_sqm <= max_area)
    if featured is not None:
        result = result.filter(Property.featured.is_(featured))
    if query and query.strip():
        pattern = f"%{query.strip()}%"
        result = result.filter(
            or_(Property.title.ilike(pattern), Property.description.ilike(pattern))
        )

    total = result.count()
    order_map = {
        "price_asc": Property.price.asc(),
        "price_desc": Property.price.desc(),
        "area_desc": Property.area_sqm.desc(),
        "recent": Property.created_at.desc(),
    }
    properties = (
        result.order_by(order_map[sort]).offset(offset).limit(limit).all()
    )
    favorite_ids = _favorite_ids(db, current_user)
    items = [
        property_to_dict(prop, is_favorite=prop.id in favorite_ids)
        for prop in properties
    ]

    if not with_meta:
        return items
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_next": offset + len(items) < total,
        "has_previous": offset > 0,
    }


@router.get("/properties/mine", response_model=List[PropertyOut])
def get_my_properties(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista anúncios ativos pertencentes ao usuário autenticado."""
    properties = (
        db.query(Property)
        .filter(
            Property.owner_id == current_user.id,
            Property.is_active.is_(True),
        )
        .order_by(Property.created_at.desc())
        .all()
    )
    favorite_ids = _favorite_ids(db, current_user)
    return [
        property_to_dict(prop, is_favorite=prop.id in favorite_ids)
        for prop in properties
    ]


@router.get("/properties/{property_id}", response_model=PropertyOut)
def get_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Retorna os detalhes de um imóvel ativo."""
    prop = db.get(Property, property_id)
    if prop is None or not prop.is_active:
        raise HTTPException(
            status_code=404, detail=f"Imóvel com ID {property_id} não encontrado."
        )
    favorite_ids = _favorite_ids(db, current_user)
    return property_to_dict(prop, is_favorite=property_id in favorite_ids)


@router.post("/properties", response_model=PropertyOut, status_code=201)
def create_property(
    property_data: PropertyIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cria um anúncio vinculado ao usuário autenticado."""
    prop = Property(
        **property_data.model_dump(),
        owner_id=current_user.id,
    )
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return property_to_dict(prop)


@router.put("/properties/{property_id}", response_model=PropertyOut)
def update_property(
    property_id: int,
    property_data: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Edita um anúncio pertencente ao usuário autenticado."""
    prop = _require_owned_property(db, property_id, current_user)
    updates = property_data.model_dump(exclude_unset=True, exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Nenhuma alteração informada.")
    for field, value in updates.items():
        setattr(prop, field, value)
    db.commit()
    db.refresh(prop)
    favorite_ids = _favorite_ids(db, current_user)
    return property_to_dict(prop, is_favorite=prop.id in favorite_ids)


@router.delete("/properties/{property_id}", response_model=ActionResponse)
def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Desativa um anúncio sem apagar seu histórico do banco."""
    prop = _require_owned_property(db, property_id, current_user)
    prop.is_active = False
    db.commit()
    return {
        "success": True,
        "message": "Imóvel excluído com sucesso.",
        "action": "delete",
        "affected_id": property_id,
    }


@router.get("/stats", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db)):
    """Calcula estatísticas reais a partir do banco de dados."""
    active = Property.is_active.is_(True)
    available = db.query(Property).filter(active).count()
    for_sale = (
        db.query(Property)
        .filter(active, Property.purpose == "comprar")
        .count()
    )
    for_rent = (
        db.query(Property)
        .filter(active, Property.purpose == "alugar")
        .count()
    )
    launches = (
        db.query(Property)
        .filter(active, Property.purpose == "lancamento")
        .count()
    )
    type_rows = (
        db.query(Property.property_type, func.count(Property.id))
        .filter(active)
        .group_by(Property.property_type)
        .all()
    )
    total_users = db.query(User).count()
    total_favorites = (
        db.query(Favorite)
        .join(Property, Property.id == Favorite.property_id)
        .filter(active)
        .count()
    )
    return {
        "available_properties": available,
        "for_sale": for_sale,
        "for_rent": for_rent,
        "launches": launches,
        "total_users": total_users,
        "total_favorites": total_favorites,
        "sold_properties": 0,
        "happy_clients": total_users,
        "years_experience": date.today().year - 2010,
        "by_type": {name: count for name, count in type_rows},
    }
