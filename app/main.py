"""Aplicação FastAPI do ImóvelFácil."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import SessionLocal
from app.routers import auth, favorites, properties
from app.seed import seed_if_empty

API_VERSION = "1.1.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas e popula com dados de exemplo na primeira execução
    with SessionLocal() as db:
        seed_if_empty(db)
    yield


app = FastAPI(
    title="ImóvelFácil API",
    description="API do portal imobiliário ImóvelFácil",
    version=API_VERSION,
    lifespan=lifespan,
)

# Habilita CORS para o frontend React (Vite roda em http://localhost:5173).
# Em desenvolvimento o Vite faz proxy de /api para a porta 8000;
# em produção o front publicado no GitHub Pages acessa a API diretamente.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://augustocampos1970.github.io",
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


@app.get("/api/health")
def health_check():
    """Health check da API: retorna status e versão atual."""
    return {"status": "ok", "version": API_VERSION}
