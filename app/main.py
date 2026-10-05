"""Aplicação FastAPI do ImóvelFácil."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import SessionLocal
from app.routers import auth, favorites, properties
from app.seed import seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas e popula com dados de exemplo na primeira execução
    with SessionLocal() as db:
        seed_if_empty(db)
    yield


app = FastAPI(
    title="ImóvelFácil API",
    description="API do portal imobiliário ImóvelFácil",
    version="1.0.0",
    lifespan=lifespan,
)

# Habilita CORS para o frontend React (Vite roda em http://localhost:5173).
# Em desenvolvimento o Vite faz proxy de /api para a porta 8000;
# estas origens cobrem o caso em que o front acessa a API diretamente.
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

app.include_router(properties.router)
app.include_router(favorites.router)
app.include_router(auth.router)


@app.get("/")
def root():
    """Endpoint de verificação de saúde da API."""
    return {"message": "ImóvelFácil API funcionando! Acesse /docs para a documentação."}
