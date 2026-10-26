-- ImóvelFácil - schema PostgreSQL compatível com os modelos SQLAlchemy 1.2.0
-- Para uma instalação que usou o schema UUID antigo, faça backup e migre/recrie
-- as tabelas antes de executar este arquivo. Este script não apaga dados.

CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(160) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.properties (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    property_type VARCHAR(50) NOT NULL,
    purpose VARCHAR(50) NOT NULL DEFAULT 'comprar',
    price DOUBLE PRECISION NOT NULL CHECK (price > 0),
    bedrooms INTEGER NOT NULL DEFAULT 0 CHECK (bedrooms >= 0),
    bathrooms INTEGER NOT NULL DEFAULT 0 CHECK (bathrooms >= 0),
    area_sqm DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (area_sqm >= 0),
    location VARCHAR(255) NOT NULL,
    neighborhood VARCHAR(150) NOT NULL DEFAULT '',
    city VARCHAR(150) NOT NULL,
    state VARCHAR(2) NOT NULL CHECK (char_length(state) = 2),
    image_url TEXT NOT NULL DEFAULT '',
    featured BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    owner_id INTEGER REFERENCES public.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.favorites (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES public.properties(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_favorites_property_user UNIQUE (property_id, user_id)
);

CREATE INDEX IF NOT EXISTS ix_users_email
    ON public.users (email);
CREATE INDEX IF NOT EXISTS ix_properties_property_type
    ON public.properties (property_type);
CREATE INDEX IF NOT EXISTS ix_properties_purpose
    ON public.properties (purpose);
CREATE INDEX IF NOT EXISTS ix_properties_price
    ON public.properties (price);
CREATE INDEX IF NOT EXISTS ix_properties_bedrooms
    ON public.properties (bedrooms);
CREATE INDEX IF NOT EXISTS ix_properties_city
    ON public.properties (city);
CREATE INDEX IF NOT EXISTS ix_properties_state
    ON public.properties (state);
CREATE INDEX IF NOT EXISTS ix_properties_neighborhood
    ON public.properties (neighborhood);
CREATE INDEX IF NOT EXISTS ix_properties_owner_id
    ON public.properties (owner_id);
CREATE INDEX IF NOT EXISTS ix_properties_active_recent
    ON public.properties (is_active, created_at DESC);
CREATE INDEX IF NOT EXISTS ix_properties_purpose_price
    ON public.properties (purpose, price);
CREATE INDEX IF NOT EXISTS ix_properties_area
    ON public.properties (area_sqm);
CREATE INDEX IF NOT EXISTS ix_favorites_property_id
    ON public.favorites (property_id);
CREATE INDEX IF NOT EXISTS ix_favorites_user_id
    ON public.favorites (user_id);

-- A autenticação desta aplicação é controlada pela API FastAPI com token Bearer.
-- Em Supabase, não exponha estas tabelas diretamente ao cliente pelo PostgREST.
-- A conexão DATABASE_URL deve ser usada somente pelo serviço backend.
