"""Modelos Pydantic (entrada/saída da API)."""

from pydantic import BaseModel, Field


class PropertyIn(BaseModel):
    """Dados de entrada para criação de imóvel."""

    title: str
    description: str = ""
    property_type: str = Field(description="Casa, Apartamento, Cobertura, Terreno")
    purpose: str = Field(default="comprar", description="comprar, alugar, lancamento")
    price: float
    location: str
    neighborhood: str = ""
    city: str
    state: str
    bedrooms: int = 0
    bathrooms: int = 0
    area_sqm: int = 0
    image_url: str = ""
    featured: bool = False


class FavoriteToggle(BaseModel):
    """Alterna o status de favorito de um imóvel."""

    property_id: int
    is_favorite: bool


class UserRegister(BaseModel):
    """Cadastro de usuário."""

    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    """Login de usuário."""

    email: str
    password: str
