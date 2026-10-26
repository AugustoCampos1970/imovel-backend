"""Configurações da aplicação."""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Banco padrão local: SQLite em imovelfacil.db (dentro da raiz do repositório).
# Em produção, defina DATABASE_URL para um PostgreSQL persistente.
DATABASE_URL = os.getenv(
    "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'imovelfacil.db')}"
)

# Tokens de acesso assinados com HMAC-SHA256.
# Em produção, JWT_SECRET_KEY deve ser um segredo longo configurado no provedor.
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "imovelfacil-dev-secret-change-in-production"
)
JWT_EXPIRE_SECONDS = int(os.getenv("JWT_EXPIRE_SECONDS", "86400"))
