"""
ImóvelFácil - Backend API
=========================
Portal imobiliário construído com FastAPI + Uvicorn + SQLAlchemy.

Endpoints:
- GET  /api/properties        → Lista imóveis com filtros (tipo, finalidade, preço, localização, quartos, palavra-chave)
- GET  /api/properties/{id}   → Detalhes de um imóvel específico
- POST /api/properties        → Cria um novo imóvel
- POST /api/favorites         → Alterna status de favorito de um imóvel
- POST /api/auth/register     → Cadastra um novo usuário
- POST /api/auth/login        → Login de usuário
- GET  /api/stats             → Estatísticas do portal

Banco de dados:
- Padrão local: SQLite (arquivo imovelfacil.db criado automaticamente)
- Para PostgreSQL/Supabase, defina a variável de ambiente DATABASE_URL

Execução:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000
"""

from app.main import app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
