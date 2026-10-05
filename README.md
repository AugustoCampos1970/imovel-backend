# ⚙️ Imóvel — Backend

API do portal imobiliário ImóvelFácil (FastAPI + SQLAlchemy).

## 🛠️ Tecnologias

- Python 3.14
- FastAPI
- SQLAlchemy 2.x
- SQLite (banco local) ou PostgreSQL/Supabase (via `DATABASE_URL`)

## 🚀 Como rodar localmente

```bash
# 1. Criar ambiente virtual (uma vez)
python -m venv venv
venv\Scripts\activate   # Windows

# 2. Instalar dependências (uma vez)
pip install -r requirements.txt

# 3. Rodar o servidor
uvicorn main:app --reload --port 8000
```

Na primeira execução, o banco `imovelfacil.db` é criado automaticamente e populado com 12 imóveis de exemplo e 1 usuário de teste.

## 🔗 Banco de dados

- **Local (padrão):** SQLite em `imovelfacil.db` (arquivo local, não versionado pelo Git).
- **Produção (PostgreSQL/Supabase):** defina a variável de ambiente `DATABASE_URL` antes de rodar:

```bash
export DATABASE_URL="postgresql+psycopg2://user:senha@host:5432/imovefacil"
```

O script `database.sql` contém o schema para PostgreSQL/Supabase (com RLS).

## 📁 Estrutura

```
imovel-backend/
├── main.py              # Ponto de entrada (uvicorn main:app)
├── requirements.txt     # Dependências Python
├── database.sql         # Schema PostgreSQL/Supabase (referência)
├── imovelfacil.db       # Banco local (criado automaticamente, não versionado)
└── app/
    ├── main.py          # App FastAPI + CORS + lifespan (seed)
    ├── config.py        # DATABASE_URL e constantes
    ├── database.py      # Engine + sessão SQLAlchemy
    ├── models.py        # Tabelas: users, properties, favorites
    ├── schemas.py       # Modelos Pydantic
    ├── security.py      # Hash de senha (PBKDF2)
    ├── seed.py          # Dados de exemplo (seed no primeiro startup)
    └── routers/
        ├── properties.py # GET/POST /api/properties, GET /api/stats
        ├── favorites.py # POST /api/favorites
        └── auth.py      # POST /api/auth/register | /login, GET /api/auth/users
```

## 🧪 Endpoints (Postman)

Documentação interativa: http://localhost:8000/docs

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Saúde da API |
| GET | `/api/properties` | Lista imóveis (filtros: `property_type`, `purpose`, `max_price`, `location`, `bedrooms`, `query`) |
| GET | `/api/properties/{id}` | Detalhes de um imóvel |
| POST | `/api/properties` | Cria um imóvel |
| POST | `/api/favorites` | Alterna favorito (`{property_id, is_favorite}`) |
| POST | `/api/auth/register` | Cadastro de usuário |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/users` | Lista usuários (dev) |
| GET | `/api/stats` | Estatísticas do portal |

Usuário de teste seed: `augusto@email.com` / `123456`.

## 📨 Exemplo de payload (POST /api/properties)

```json
{
  "title": "Casa com piscina no bairro Jardim América",
  "description": "Casa de 4 quartos, 3 banheiros, área de 300m² com piscina.",
  "property_type": "Casa",
  "purpose": "comprar",
  "price": 1250000.00,
  "location": "Rua das Acácias, 100 - Jardim América",
  "neighborhood": "Jardim América",
  "city": "Goiânia",
  "state": "GO",
  "bedrooms": 4,
  "bathrooms": 3,
  "area_sqm": 300,
  "featured": true
}
```

A listagem aceita paginação: `GET /api/properties?limit=20&offset=40` (padrão `limit=50`).

## 🔐 Autenticação

O cadastro e o login retornam um `token` de sessão com validade de **24 horas** (`expires_in: 86400` segundos). O token deve ser enviado no header `Authorization` em requisições autenticadas futuras.

## 🔗 Repositório do Frontend

[imovel-frontend](https://github.com/AugustoCampos1970/imovel-frontend)
