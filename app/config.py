"""Configurações da aplicação."""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Banco padrão local: SQLite em imovelfacil.db (dentro da raiz do repositório).
# Para PostgreSQL/Supabase, defina DATABASE_URL, ex.:
#   postgresql+psycopg2://usuario:senha@host:5432/imovefacil
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'imovelfacil.db')}")

# Identificador do usuário padrão para favoritos.
# Enquanto o frontend não envia token de sessão, favoritos ficam vinculados a ele.
GUEST_USER = "guest"
