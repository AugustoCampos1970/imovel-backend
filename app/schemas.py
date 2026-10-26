"""Modelos Pydantic de entrada e saída da API."""

import re
from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

PropertyType = Literal["Casa", "Apartamento", "Cobertura", "Terreno"]
PropertyPurpose = Literal["comprar", "alugar", "lancamento"]


class PropertyIn(BaseModel):
    """Dados de entrada para criação de imóvel."""

    title: str = Field(min_length=3, max_length=255)
    description: str = Field(default="", max_length=5000)
    property_type: PropertyType
    purpose: PropertyPurpose = "comprar"
    price: float = Field(gt=0)
    location: str = Field(min_length=3, max_length=255)
    neighborhood: str = Field(default="", max_length=150)
    city: str = Field(min_length=2, max_length=150)
    state: str = Field(min_length=2, max_length=2)
    bedrooms: int = Field(default=0, ge=0)
    bathrooms: int = Field(default=0, ge=0)
    area_sqm: float = Field(default=0, ge=0)
    image_url: str = Field(default="", max_length=2000)
    featured: bool = False

    @field_validator("title", "location", "city")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("O campo não pode ficar vazio.")
        return value

    @field_validator("description", "neighborhood", "image_url")
    @classmethod
    def strip_optional_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("state")
    @classmethod
    def normalize_state(cls, value: str) -> str:
        value = value.strip().upper()
        if not re.fullmatch(r"[A-Z]{2}", value):
            raise ValueError("A UF deve conter exatamente duas letras.")
        return value


class PropertyUpdate(BaseModel):
    """Campos opcionais aceitos na edição de um imóvel."""

    title: Optional[str] = Field(default=None, min_length=3, max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)
    property_type: Optional[PropertyType] = None
    purpose: Optional[PropertyPurpose] = None
    price: Optional[float] = Field(default=None, gt=0)
    location: Optional[str] = Field(default=None, min_length=3, max_length=255)
    neighborhood: Optional[str] = Field(default=None, max_length=150)
    city: Optional[str] = Field(default=None, min_length=2, max_length=150)
    state: Optional[str] = Field(default=None, min_length=2, max_length=2)
    bedrooms: Optional[int] = Field(default=None, ge=0)
    bathrooms: Optional[int] = Field(default=None, ge=0)
    area_sqm: Optional[float] = Field(default=None, ge=0)
    image_url: Optional[str] = Field(default=None, max_length=2000)
    featured: Optional[bool] = None

    @field_validator("title", "location", "city")
    @classmethod
    def validate_optional_required_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("O campo não pode ficar vazio.")
        return value

    @field_validator("description", "neighborhood", "image_url")
    @classmethod
    def strip_optional_text(cls, value: Optional[str]) -> Optional[str]:
        return value.strip() if value is not None else value

    @field_validator("state")
    @classmethod
    def normalize_optional_state(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip().upper()
        if not re.fullmatch(r"[A-Z]{2}", value):
            raise ValueError("A UF deve conter exatamente duas letras.")
        return value


class PropertyOut(BaseModel):
    id: int
    title: str
    description: str
    property_type: str
    purpose: str
    price: float
    location: str
    neighborhood: str
    city: str
    state: str
    bedrooms: int
    bathrooms: int
    area_sqm: float
    image_url: str
    featured: bool
    is_favorite: bool = False
    owner_id: Optional[int] = None
    created_at: Optional[datetime] = None


class PaginatedProperties(BaseModel):
    items: List[PropertyOut]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_previous: bool


class FavoriteToggle(BaseModel):
    """Alterna o status de favorito de um imóvel."""

    property_id: int = Field(gt=0)
    is_favorite: bool


class FavoriteResult(BaseModel):
    property_id: int
    is_favorite: bool
    message: str


class UserRegister(BaseModel):
    """Cadastro de usuário."""

    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=160)
    password: str = Field(min_length=6, max_length=128)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return " ".join(value.strip().split())

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("Informe um e-mail válido.")
        return value


class UserLogin(BaseModel):
    """Login de usuário."""

    email: str = Field(min_length=5, max_length=160)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserPublic(BaseModel):
    id: int
    name: str
    email: str
    created_at: Optional[datetime] = None


class AuthResponse(UserPublic):
    token: str
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    message: str


class StatsOut(BaseModel):
    available_properties: int
    for_sale: int
    for_rent: int
    launches: int
    total_users: int
    total_favorites: int
    sold_properties: int = 0
    happy_clients: int
    years_experience: int
    by_type: Dict[str, int]


class MessageOut(BaseModel):
    message: str
