"""Rotas de imóveis (listagem, detalhes, criação) e estatísticas."""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.config import GUEST_USER
from app.database import get_db
from app.models import Favorite, Property
from app.schemas import PropertyIn

router = APIRouter(prefix="/api", tags=["properties"])


def _property_to_dict(prop: Property, is_favorite: bool = False) -> dict:
    """Converte o modelo SQLAlchemy para o formato JSON esperado pelo frontend."""
    return {
        "id": prop.id,
        "title": prop.title,
        "description": prop.description,
        "property_type": prop.property_type,
        "purpose": prop.purpose,
        "price": prop.price,
        "location": prop.location,
        "neighborhood": prop.neighborhood,
        "city": prop.city,
        "state": prop.state,
        "bedrooms": prop.bedrooms,
        "bathrooms": prop.bathrooms,
        "area_sqm": prop.area_sqm,
        "image_url": prop.image_url,
        "featured": prop.featured,
        "is_favorite": is_favorite,
        "created_at": prop.created_at.isoformat() if prop.created_at else None,
    }


def _favorite_ids(db: Session) -> set:
    return {
        row.property_id
        for row in db.query(Favorite.property_id).filter(
            Favorite.user_id == GUEST_USER
        )
    }


@router.get("/properties", response_model=List[dict])
def get_properties(
    property_type: Optional[str] = Query(None, description="Tipo de imóvel: Casa, Apartamento, Cobertura, Terreno"),
    purpose: Optional[str] = Query(None, description="Finalidade: comprar, alugar, lancamento"),
    max_price: Optional[float] = Query(None, description="Preço máximo (filtro)"),
    location: Optional[str] = Query(None, description="Localização: cidade ou bairro"),
    bedrooms: Optional[int] = Query(None, description="Número mínimo de quartos"),
    query: Optional[str] = Query(None, description="Palavra-chave (título/descrição)"),
    limit: int = Query(50, ge=1, le=200, description="Limite de itens por página"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    db: Session = Depends(get_db),
):
    """
    Lista os imóveis disponíveis aplicando os filtros de busca.

    Exemplos de uso:
    - GET /api/properties?property_type=Casa
    - GET /api/properties?purpose=alugar&max_price=3000
    - GET /api/properties?location=Pinheiros
    - GET /api/properties?bedrooms=3&query=piscina
    - GET /api/properties?limit=20&offset=40
    """
    q = db.query(Property).filter(Property.is_active.is_(True))

    if property_type and property_type.lower() != "todos":
        q = q.filter(func.lower(Property.property_type) == property_type.lower())

    if purpose and purpose.lower() != "todos":
        q = q.filter(func.lower(Property.purpose) == purpose.lower())

    if max_price is not None and max_price > 0:
        q = q.filter(Property.price <= max_price)

    if location and location.strip():
        pattern = f"%{location.strip().lower()}%"
        q = q.filter(
            or_(
                Property.location.ilike(pattern),
                Property.neighborhood.ilike(pattern),
                Property.city.ilike(pattern),
            )
        )

    if bedrooms is not None and bedrooms > 0:
        q = q.filter(Property.bedrooms >= bedrooms)

    if query and query.strip():
        pattern = f"%{query.strip().lower()}%"
        q = q.filter(
            or_(Property.title.ilike(pattern), Property.description.ilike(pattern))
        )

    favorite_ids = _favorite_ids(db)
    return [
        _property_to_dict(prop, is_favorite=prop.id in favorite_ids)
        for prop in q.offset(offset).limit(limit).all()
    ]


@router.get("/properties/{property_id}", response_model=dict)
def get_property(property_id: int, db: Session = Depends(get_db)):
    """Retorna os detalhes de um imóvel específico pelo ID."""
    prop = db.get(Property, property_id)
    if prop is None:
        raise HTTPException(
            status_code=404, detail=f"Imóvel com ID {property_id} não encontrado."
        )

    favorite_ids = _favorite_ids(db)
    return _property_to_dict(prop, is_favorite=property_id in favorite_ids)


@router.post("/properties", response_model=dict, status_code=201)
def create_property(property_data: PropertyIn, db: Session = Depends(get_db)):
    """Cria um novo imóvel (utilizado pelo formulário "Anunciar" no frontend)."""
    if not property_data.title.strip():
        raise HTTPException(status_code=400, detail="O título do imóvel é obrigatório.")
    if not property_data.location.strip() or not property_data.city.strip():
        raise HTTPException(status_code=400, detail="Localização e cidade são obrigatórias.")
    if property_data.price <= 0:
        raise HTTPException(status_code=400, detail="O preço deve ser maior que zero.")
    if (
        property_data.bedrooms < 0
        or property_data.bathrooms < 0
        or property_data.area_sqm < 0
    ):
        raise HTTPException(
            status_code=400,
            detail="Quartos, banheiros e área não podem ser negativos.",
        )

    prop = Property(**property_data.model_dump())
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return _property_to_dict(prop)


@router.get("/stats", response_model=dict)
def get_stats():
    """Retorna estatísticas do portal para a Hero Section."""
    return {
        "available_properties": 5000,
        "sold_properties": 2500,
        "happy_clients": 10000,
        "years_experience": date.today().year - 2010,
    }
