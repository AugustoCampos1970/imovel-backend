"""Conversores dos modelos de banco para respostas da API."""

from app.models import Property


def property_to_dict(prop: Property, is_favorite: bool = False) -> dict:
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
        "owner_id": prop.owner_id,
        "created_at": prop.created_at,
    }
