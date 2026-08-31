"""
ImóvelFácil - Backend API
=========================
Portal imobiliário construído com FastAPI + Uvicorn.

Endpoints:
- GET /api/properties        → Lista imóveis com filtros (tipo, finalidade, preço, localização)
- GET /api/properties/{id}   → Detalhes de um imóvel específico
- POST /api/favorites        → Alterna status de favorito de um imóvel

Execução:
    uvicorn main:app --reload --port 8000
"""

from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Configuração da Aplicação
# ---------------------------------------------------------------------------
app = FastAPI(
    title="ImóvelFácil API",
    description="API do portal imobiliário ImóvelFácil",
    version="1.0.0",
)

# Habilita CORS para o frontend React (Vite roda em http://localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Modelos (Pydantic)
# ---------------------------------------------------------------------------
class PropertyIn(BaseModel):
    """Modelo de entrada para criação de imóvel."""
    title: str
    description: str
    property_type: str            # casa, apartamento, cobertura, terreno
    purpose: str                 # comprar, alugar, lancamento
    price: float
    location: str
    neighborhood: str
    city: str
    state: str
    bedrooms: int
    bathrooms: int
    area_sqm: int
    image_url: str
    featured: bool = False


class FavoriteToggle(BaseModel):
    """Modelo para alternar status de favorito."""
    property_id: int
    is_favorite: bool


class UserRegister(BaseModel):
    """Modelo de entrada para cadastro de usuário."""
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    """Modelo de entrada para login de usuário."""
    email: str
    password: str


# ---------------------------------------------------------------------------
# Mock Data - Imóveis de exemplo para testes sem banco de dados
# ---------------------------------------------------------------------------
MOCK_PROPERTIES = [
    {
        "id": 1,
        "title": "Casa Moderna com Piscina no Jardim Europa",
        "description": "Casa ampla em condomínio fechado, com 4 suítes, piscina aquecida, jardim privativo e área gourmet completa. Acabamento de alto padrão.",
        "property_type": "Casa",
        "purpose": "comprar",
        "price": 1250000.00,
        "location": "Jardim Europa, São Paulo",
        "neighborhood": "Jardim Europa",
        "city": "São Paulo",
        "state": "SP",
        "bedrooms": 4,
        "bathrooms": 5,
        "area_sqm": 420,
        "image_url": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&q=80",
        "featured": True,
    },
    {
        "id": 2,
        "title": "Apartamento Alto Padrão com Vista para o Mar",
        "description": "Apartamento de luxo com 3 suítes, varanda gourmet e vista panorâmica para o mar. Prédio com lazer completo: piscina, academia e salão de festas.",
        "property_type": "Apartamento",
        "purpose": "comprar",
        "price": 980000.00,
        "location": "Orla da Praia, Santos",
        "neighborhood": "Orla da Praia",
        "city": "Santos",
        "state": "SP",
        "bedrooms": 3,
        "bathrooms": 4,
        "area_sqm": 180,
        "image_url": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&q=80",
        "featured": True,
    },
    {
        "id": 3,
        "title": "Cobertura Duplex com Terraço Privativo",
        "description": "Cobertura duplex com terraço de 80m², churrasqueira e vista deslumbrante. Localização privilegiada a poucos minutos do metrô.",
        "property_type": "Cobertura",
        "purpose": "comprar",
        "price": 2100000.00,
        "location": "Moema, São Paulo",
        "neighborhood": "Moema",
        "city": "São Paulo",
        "state": "SP",
        "bedrooms": 4,
        "bathrooms": 5,
        "area_sqm": 310,
        "image_url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&q=80",
        "featured": True,
    },
    {
        "id": 4,
        "title": "Terreno 500m² em Condomínio Fechado",
        "description": "Terreno plano de 500m² em condomínio fechado com segurança 24h, infraestrutura completa e área de lazer. Perfeito para construir sua casa dos sonhos.",
        "property_type": "Terreno",
        "purpose": "comprar",
        "price": 350000.00,
        "location": "Alphaville, Barueri",
        "neighborhood": "Alphaville",
        "city": "Barueri",
        "state": "SP",
        "bedrooms": 0,
        "bathrooms": 0,
        "area_sqm": 500,
        "image_url": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800&q=80",
        "featured": False,
    },
    {
        "id": 5,
        "title": "Apartamento 2 Quartos com Varanda Encantadora",
        "description": "Apartamento aconchegante com 2 quartos, varanda, vaga de garagem e condomínio com lazer completo. Ótima oportunidade para primeira moradia.",
        "property_type": "Apartamento",
        "purpose": "alugar",
        "price": 2800.00,
        "location": "Pinheiros, São Paulo",
        "neighborhood": "Pinheiros",
        "city": "São Paulo",
        "state": "SP",
        "bedrooms": 2,
        "bathrooms": 2,
        "area_sqm": 68,
        "image_url": "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800&q=80",
        "featured": False,
    },
    {
        "id": 6,
        "title": "Casa com Jardim no Bairro dos Estados",
        "description": "Casa charmosa com 3 quartos, jardim frontal, quintal espaçoso e garagem para 2 carros. Bairro tranquilo e familiar.",
        "property_type": "Casa",
        "purpose": "alugar",
        "price": 4500.00,
        "location": "Bairro dos Estados, Campinas",
        "neighborhood": "Bairro dos Estados",
        "city": "Campinas",
        "state": "SP",
        "bedrooms": 3,
        "bathrooms": 3,
        "area_sqm": 160,
        "image_url": "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800&q=80",
        "featured": False,
    },
    {
        "id": 7,
        "title": "Lançamento Studio Mobiliado no Centro",
        "description": "Studio mobiliado de 32m² com design inteligente. Prédio com rooftop, coworking e academia. Perfeito para investidores.",
        "property_type": "Apartamento",
        "purpose": "lancamento",
        "price": 420000.00,
        "location": "Centro, São Paulo",
        "neighborhood": "Centro",
        "city": "São Paulo",
        "state": "SP",
        "bedrooms": 1,
        "bathrooms": 1,
        "area_sqm": 32,
        "image_url": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&q=80",
        "featured": True,
    },
    {
        "id": 8,
        "title": "Lançamento Apartamento 3 Quartos com Lazer Premium",
        "description": "Lançamento exclusivo com apartamentos de 3 quartos sendo 1 suíte, varanda e lazer premium: piscina coberta, quadra, playground e espaço gourmet.",
        "property_type": "Apartamento",
        "purpose": "lancamento",
        "price": 750000.00,
        "location": "Vila Olímpia, São Paulo",
        "neighborhood": "Vila Olímpia",
        "city": "São Paulo",
        "state": "SP",
        "bedrooms": 3,
        "bathrooms": 3,
        "area_sqm": 120,
        "image_url": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&q=80",
        "featured": True,
    },
    {
        "id": 9,
        "title": "Casa de Campo com Área de Lazer Completa",
        "description": "Casa de campo com 3 suítes, piscina, churrasqueira e 2.000m² de área verde. Perfeita para fins de semana ou moradia.",
        "property_type": "Casa",
        "purpose": "comprar",
        "price": 1650000.00,
        "location": "Bairro das Palmeiras, Campos do Jordão",
        "neighborhood": "Bairro das Palmeiras",
        "city": "Campos do Jordão",
        "state": "SP",
        "bedrooms": 3,
        "bathrooms": 4,
        "area_sqm": 380,
        "image_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&q=80",
        "featured": False,
    },
    {
        "id": 10,
        "title": "Terreno 800m² com Vista para o Vale",
        "description": "Terreno de 800m² com vista privilegiada para o vale, acesso fácil e documentação em dia. Ótima oportunidade de investimento.",
        "property_type": "Terreno",
        "purpose": "comprar",
        "price": 480000.00,
        "location": "Vale do Sol, Campinas",
        "neighborhood": "Vale do Sol",
        "city": "Campinas",
        "state": "SP",
        "bedrooms": 0,
        "bathrooms": 0,
        "area_sqm": 800,
        "image_url": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800&q=80",
        "featured": False,
    },
    {
        "id": 11,
        "title": "Apartamento 1 Quarto Mobiliado Próximo ao Metrô",
        "description": "Apartamento mobiliado de 45m² com 1 quarto, próximo ao metrô e comércios. Ideal para quem busca praticidade no dia a dia.",
        "property_type": "Apartamento",
        "purpose": "alugar",
        "price": 1900.00,
        "location": "Vila Mariana, São Paulo",
        "neighborhood": "Vila Mariana",
        "city": "São Paulo",
        "state": "SP",
        "bedrooms": 1,
        "bathrooms": 1,
        "area_sqm": 45,
        "image_url": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&q=80",
        "featured": False,
    },
    {
        "id": 12,
        "title": "Cobertura com Área Gourmet e Vista Incrível",
        "description": "Cobertura com área gourmet de 40m², hidromassagem e vista para a cidade. Mais completa com 3 suítes e vapor.",
        "property_type": "Cobertura",
        "purpose": "comprar",
        "price": 1500000.00,
        "location": "Jardim Paulista, São Paulo",
        "neighborhood": "Jardim Paulista",
        "city": "São Paulo",
        "state": "SP",
        "bedrooms": 3,
        "bathrooms": 4,
        "area_sqm": 240,
        "image_url": "https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?w=800&q=80",
        "featured": True,
    },
]

# Estado de favoritos (simulado em memória)
# Em produção, utilize o banco de dados PostgreSQL/Supabase via tabela `favorites`
MOCK_FAVORITES: set = {1, 3, 5}

# Estado de usuários (simulado em memória)
# Em produção, utilize uma tabela `users` no PostgreSQL/Supabase
MOCK_USERS: list = [
    {
        "id": 1,
        "name": "Augusto Silva",
        "email": "augusto@email.com",
        "password": "123456",
    }
]
_user_id_counter: int = 2


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _apply_filters(
    items: List[dict],
    property_type: Optional[str],
    purpose: Optional[str],
    max_price: Optional[float],
    location: Optional[str],
    bedrooms: Optional[int],
) -> List[dict]:
    """Aplica os filtros de busca sobre a lista de imóveis."""
    filtered = items

    if property_type and property_type.lower() != "todos":
        filtered = [p for p in filtered if p["property_type"].lower() == property_type.lower()]

    if purpose and purpose.lower() != "todos":
        filtered = [p for p in filtered if p["purpose"].lower() == purpose.lower()]

    if max_price is not None and max_price > 0:
        filtered = [p for p in filtered if p["price"] <= max_price]

    if location and location.strip():
        location_lower = location.strip().lower()
        filtered = [
            p
            for p in filtered
            if location_lower in p["location"].lower()
            or location_lower in p["neighborhood"].lower()
            or location_lower in p["city"].lower()
        ]

    if bedrooms is not None and bedrooms > 0:
        filtered = [p for p in filtered if p["bedrooms"] >= bedrooms]

    return filtered


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/")
async def root():
    """Endpoint de verificação de saúde da API."""
    return {"message": "ImóvelFácil API funcionando! Acesse /docs para a documentação."}


@app.get("/api/properties", response_model=List[dict])
async def get_properties(
    property_type: Optional[str] = Query(None, description="Tipo de imóvel: Casa, Apartamento, Cobertura, Terreno"),
    purpose: Optional[str] = Query(None, description="Finalidade: comprar, alugar, lancamento"),
    max_price: Optional[float] = Query(None, description="Preço máximo (filtro)"),
    location: Optional[str] = Query(None, description="Localização: cidade ou bairro"),
    bedrooms: Optional[int] = Query(None, description="Número mínimo de quartos"),
):
    """
    Lista os imóveis disponíveis aplicando os filtros de busca.

    Exemplos de uso:
    - GET /api/properties?property_type=Casa
    - GET /api/properties?purpose=alugar&max_price=3000
    - GET /api/properties?location=Pinheiros
    - GET /api/properties?bedrooms=3
    """
    properties = _apply_filters(
        items=MOCK_PROPERTIES,
        property_type=property_type,
        purpose=purpose,
        max_price=max_price,
        location=location,
        bedrooms=bedrooms,
    )

    # Adiciona o campo is_favorite para cada imóvel
    result = []
    for prop in properties:
        prop_with_fav = {**prop, "is_favorite": prop["id"] in MOCK_FAVORITES}
        result.append(prop_with_fav)

    return result


@app.get("/api/properties/{property_id}", response_model=dict)
async def get_property(property_id: int):
    """
    Retorna os detalhes de um imóvel específico pelo ID.
    """
    for prop in MOCK_PROPERTIES:
        if prop["id"] == property_id:
            return {**prop, "is_favorite": property_id in MOCK_FAVORITES}

    raise HTTPException(status_code=404, detail=f"Imóvel com ID {property_id} não encontrado.")


@app.post("/api/favorites", response_model=dict)
async def toggle_favorite(payload: FavoriteToggle):
    """
    Alterna o status de favorito de um imóvel.

    Body:
    {
        "property_id": 1,
        "is_favorite": true
    }

    Resposta: status atualizado do imóvel nos favoritos.
    """
    # Valida se o imóvel existe
    property_exists = any(p["id"] == payload.property_id for p in MOCK_PROPERTIES)
    if not property_exists:
        raise HTTPException(
            status_code=404,
            detail=f"Imóvel com ID {payload.property_id} não encontrado.",
        )

    # Alterna o status do favorito
    if payload.is_favorite:
        MOCK_FAVORITES.add(payload.property_id)
    else:
        MOCK_FAVORITES.discard(payload.property_id)

    return {
        "property_id": payload.property_id,
        "is_favorite": payload.is_favorite,
        "message": "Imóvel adicionado aos favoritos." if payload.is_favorite else "Imóvel removido dos favoritos.",
    }


@app.post("/api/properties", response_model=dict, status_code=201)
async def create_property(property_data: PropertyIn):
    """
    Cria um novo imóvel (utilizado pelo formulário "Anunciar" no frontend).
    """
    new_id = max(p["id"] for p in MOCK_PROPERTIES) + 1
    new_property = {
        "id": new_id,
        **property_data.model_dump(),
    }
    MOCK_PROPERTIES.append(new_property)
    return new_property


@app.get("/api/stats", response_model=dict)
async def get_stats():
    """
    Retorna estatísticas do portal para a Hero Section.
    """
    from datetime import date

    return {
        "available_properties": 5000,
        "sold_properties": 2500,
        "happy_clients": 10000,
        "years_experience": date.today().year - 2010,
    }


# ---------------------------------------------------------------------------
# Endpoints de Autenticação
# ---------------------------------------------------------------------------
def _public_user(user: dict) -> dict:
    """Remove o campo password da resposta para não expor dados sensíveis."""
    return {k: v for k, v in user.items() if k != "password"}


@app.post("/api/auth/register", response_model=dict, status_code=201)
async def register_user(payload: UserRegister):
    """
    Cadastra um novo usuário.

    Body:
    {
        "name": "Nome do usuário",
        "email": "usuario@email.com",
        "password": "123456"
    }

    Resposta: dados públicos do usuário e um token de sessão.
    """
    email = payload.email.strip().lower()

    if not payload.name.strip():
        raise HTTPException(status_code=400, detail="O nome é obrigatório.")

    if len(payload.password) < 6:
        raise HTTPException(
            status_code=400, detail="A senha deve ter pelo menos 6 caracteres."
        )

    if any(u["email"] == email for u in MOCK_USERS):
        raise HTTPException(
            status_code=409, detail="Já existe um usuário com este e-mail."
        )

    global _user_id_counter
    new_user = {
        "id": _user_id_counter,
        "name": payload.name.strip(),
        "email": email,
        "password": payload.password,
    }
    _user_id_counter += 1
    MOCK_USERS.append(new_user)

    return {
        **_public_user(new_user),
        "token": f"token-{new_user['id']}",
        "message": "Usuário cadastrado com sucesso!",
    }


@app.post("/api/auth/login", response_model=dict)
async def login_user(payload: UserLogin):
    """
    Realiza o login de um usuário existente.

    Body:
    {
        "email": "usuario@email.com",
        "password": "123456"
    }
    """
    email = payload.email.strip().lower()

    user = next((u for u in MOCK_USERS if u["email"] == email), None)
    if user is None or user["password"] != payload.password:
        raise HTTPException(
            status_code=401, detail="E-mail ou senha inválidos."
        )

    return {
        **_public_user(user),
        "token": f"token-{user['id']}",
        "message": "Login realizado com sucesso!",
    }


@app.get("/api/auth/users", response_model=List[dict])
async def list_users():
    """
    Retorna a lista de usuários cadastrados (sem senhas).
    Útil para depuração em ambiente de desenvolvimento.
    """
    return [_public_user(u) for u in MOCK_USERS]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)