# ⚙️ ImóvelFácil — Backend

API FastAPI da Entrega 4, com autenticação Bearer, anúncios por usuário, favoritos individuais, edição, exclusão lógica, filtros, paginação e estatísticas dinâmicas.

## Tecnologias

- Python 3.12+ (validado também em Python 3.14)
- FastAPI
- SQLAlchemy 2.x
- SQLite no desenvolvimento
- PostgreSQL no ambiente de produção

## Execução local

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

- Swagger: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/health`
- Usuário seed: `augusto@email.com` / `123456`

Na primeira execução, a API cria 12 imóveis. Bancos SQLite antigos recebem a coluna `owner_id` sem apagar os anúncios existentes.

## Configuração

Copie `.env.example` ou configure as variáveis no ambiente:

```env
DATABASE_URL=postgresql+psycopg2://usuario:senha@host:5432/imovefacil
JWT_SECRET_KEY=um-segredo-longo-e-aleatorio
JWT_EXPIRE_SECONDS=86400
```

Em desenvolvimento, `DATABASE_URL` é opcional e o padrão é `imovelfacil.db`. Em produção, use obrigatoriamente um PostgreSQL persistente.

O arquivo `database.sql` corresponde aos modelos SQLAlchemy atuais: IDs inteiros, tabela de usuários, proprietário do anúncio e favoritos com restrição única por usuário/imóvel.

## Autenticação

Cadastro e login retornam um JWT HS256 com validade padrão de 24 horas:

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "augusto@email.com",
  "password": "123456"
}
```

Nas rotas protegidas, envie:

```http
Authorization: Bearer <token>
```

## Endpoints da Entrega 4

| Método | Rota | Autenticação | Descrição |
|---|---|---:|---|
| GET | `/api/health` | Não | Saúde e versão da API |
| POST | `/api/auth/register` | Não | Cadastro e início da sessão |
| POST | `/api/auth/login` | Não | Login e token Bearer |
| GET | `/api/auth/me` | Sim | Usuário da sessão |
| GET | `/api/properties` | Opcional | Listagem, filtros, ordenação e paginação |
| GET | `/api/properties?with_meta=true` | Opcional | Listagem com total e indicadores de página |
| GET | `/api/properties/mine` | Sim | Anúncios do usuário |
| GET | `/api/properties/{id}` | Opcional | Detalhes do imóvel |
| POST | `/api/properties` | Sim | Cria anúncio com proprietário |
| PUT | `/api/properties/{id}` | Sim | Edita anúncio do proprietário |
| DELETE | `/api/properties/{id}` | Sim | Exclusão lógica do anúncio |
| GET | `/api/favorites` | Sim | Favoritos do usuário |
| POST | `/api/favorites` | Sim | Adiciona ou remove favorito |
| DELETE | `/api/favorites/{id}` | Sim | Remove favorito |
| GET | `/api/stats` | Não | Estatísticas reais do banco |

### Filtros de imóveis

- `property_type`, `purpose`, `query`
- `min_price`, `max_price`
- `location`, `city`, `state`
- `bedrooms`, `bathrooms`
- `min_area`, `max_area`
- `featured`
- `sort`: `recent`, `price_asc`, `price_desc`, `area_desc`
- `limit`, `offset`, `with_meta`

## Testes

Com a API na porta 8000:

```powershell
python testes_api.py
```

A suíte cobre 34 cenários: autenticação assinada, isolamento entre usuários, filtros, paginação, criação, propriedade, edição, exclusão lógica, favoritos e estatísticas.

## Deploy no Render

O `render.yaml` configura Python 3.12, health check e geração do segredo JWT. No painel do Render ainda é necessário fornecer `DATABASE_URL` com um PostgreSQL persistente.

O plano gratuito pode levar alguns segundos para acordar. O frontend apresenta uma mensagem durante esse cold start.
