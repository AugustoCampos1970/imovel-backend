-- ============================================================================
-- ImóvelFácil - Banco de Dados PostgreSQL / Supabase
-- ============================================================================
-- Este script cria as tabelas `properties` e `favorites` para o portal
-- imobiliário ImóvelFácil.
--
-- Compatível com:
--   - PostgreSQL 12+ (incluindo Supabase)
--   - Utiliza RLS (Row Level Security) para segurança no Supabase
-- ============================================================================


-- ============================================================================
-- 1. EXTENSÕES NECESSÁRIAS (Supabase já inclui por padrão)
-- ============================================================================
-- A extensão pgcrypto fornece gen_random_uuid() para geração de UUIDs
CREATE EXTENSION IF NOT EXISTS "pgcrypto";


-- ============================================================================
-- 2. TABELA: properties (imóveis)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.properties (
    -- Identificador único do imóvel
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Dados principais
    title VARCHAR(255) NOT NULL,                    -- Título do anúncio
    description TEXT NOT NULL DEFAULT '',           -- Descrição detalhada
    property_type VARCHAR(50) NOT NULL,             -- Casa, Apartamento, Cobertura, Terreno
    purpose VARCHAR(50) NOT NULL DEFAULT 'comprar', -- comprar, alugar, lancamento

    -- Preço e características
    price NUMERIC(14, 2) NOT NULL CHECK (price >= 0),  -- Preço em BRL
    bedrooms INTEGER NOT NULL DEFAULT 0 CHECK (bedrooms >= 0),
    bathrooms INTEGER NOT NULL DEFAULT 0 CHECK (bathrooms >= 0),
    area_sqm NUMERIC(10, 2) NOT NULL DEFAULT 0 CHECK (area_sqm >= 0),  -- Área em m²

    -- Localização
    location VARCHAR(255) NOT NULL,                 -- Endereço completo
    neighborhood VARCHAR(150) NOT NULL DEFAULT '',  -- Bairro
    city VARCHAR(150) NOT NULL,                     -- Cidade
    state CHAR(2) NOT NULL,                         -- UF (ex: SP, RJ, MG)

    -- Imagem e destaque
    image_url TEXT NOT NULL DEFAULT '',             -- URL da imagem principal
    featured BOOLEAN NOT NULL DEFAULT FALSE,        -- Imóvel em destaque

    -- Controle do anúncio
    is_active BOOLEAN NOT NULL DEFAULT TRUE,        -- Anúncio ativo/inativo
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),  -- Data de criação
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()   -- Data de última atualização
);


-- Índices para otimizar as buscas mais comuns
CREATE INDEX IF NOT EXISTS idx_properties_property_type ON public.properties (property_type);
CREATE INDEX IF NOT EXISTS idx_properties_purpose        ON public.properties (purpose);
CREATE INDEX IF NOT EXISTS idx_properties_price          ON public.properties (price);
CREATE INDEX IF NOT EXISTS idx_properties_city           ON public.properties (city);
CREATE INDEX IF NOT EXISTS idx_properties_neighborhood   ON public.properties (neighborhood);
CREATE INDEX IF NOT EXISTS idx_properties_bedrooms       ON public.properties (bedrooms);
CREATE INDEX IF NOT EXISTS idx_properties_featured       ON public.properties (featured) WHERE featured = TRUE;
CREATE INDEX IF NOT EXISTS idx_properties_is_active      ON public.properties (is_active);


-- ============================================================================
-- 3. TABELA: favorites (favoritos)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.favorites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relacionamento com o imóvel
    property_id UUID NOT NULL REFERENCES public.properties(id) ON DELETE CASCADE,

    -- Identificador do usuário (no Supabase, use auth.uid() no lugar de user_id)
    user_id UUID NOT NULL DEFAULT auth.uid(),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Impede que o mesmo usuário favorite o mesmo imóvel duas vezes
    CONSTRAINT uq_favorites_property_user UNIQUE (property_id, user_id)
);


-- Índices para consultas rápidas de favoritos por usuário
CREATE INDEX IF NOT EXISTS idx_favorites_user_id  ON public.favorites (user_id);
CREATE INDEX IF NOT EXISTS idx_favorites_property ON public.favorites (property_id);


-- ============================================================================
-- 4. TRIGGER: atualizar updated_at automaticamente
-- ============================================================================
-- Função que atualiza o campo updated_at antes de um UPDATE
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplica a trigger na tabela properties
DROP TRIGGER IF EXISTS trg_properties_updated_at ON public.properties;
CREATE TRIGGER trg_properties_updated_at
    BEFORE UPDATE ON public.properties
    FOR EACH ROW
    EXECUTE FUNCTION public.set_updated_at();


-- ============================================================================
-- 5. ROW LEVEL SECURITY (RLS) — Imprescindível no Supabase
-- ============================================================================
-- Habilita RLS nas tabelas
ALTER TABLE public.properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.favorites ENABLE ROW LEVEL SECURITY;


-- Políticas para properties:
-- 1) Leitura pública: qualquer usuário (anônimo ou autenticado) pode ler imóveis ativos
DROP POLICY IF EXISTS "properties_public_read" ON public.properties;
CREATE POLICY "properties_public_read"
    ON public.properties
    FOR SELECT
    USING (is_active = TRUE);

-- 2) Inserção autenticada: apenas usuários logados podem criar anúncios
--    (ajuste a condição USING conforme seu esquema de autorização, ex: usar uma coluna owner_id)
DROP POLICY IF EXISTS "properties_authenticated_insert" ON public.properties;
CREATE POLICY "properties_authenticated_insert"
    ON public.properties
    FOR INSERT
    TO authenticated
    WITH CHECK (TRUE);

-- 3) Atualização autenticada (exemplo básico — ajuste para o proprietário do anúncio)
DROP POLICY IF EXISTS "properties_authenticated_update" ON public.properties;
CREATE POLICY "properties_authenticated_update"
    ON public.properties
    FOR UPDATE
    TO authenticated
    USING (TRUE);


-- Políticas para favorites:
-- 1) Leitura: o usuário só pode ver os próprios favoritos
DROP POLICY IF EXISTS "favorites_owner_read" ON public.favorites;
CREATE POLICY "favorites_owner_read"
    ON public.favorites
    FOR SELECT
    TO authenticated
    USING (auth.uid() = user_id);

-- 2) Inserção: o usuário só pode favoritar para si mesmo
DROP POLICY IF EXISTS "favorites_owner_insert" ON public.favorites;
CREATE POLICY "favorites_owner_insert"
    ON public.favorites
    FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = user_id);

-- 3) Exclusão: o usuário só pode remover os próprios favoritos
DROP POLICY IF EXISTS "favorites_owner_delete" ON public.favorites;
CREATE POLICY "favorites_owner_delete"
    ON public.favorites
    FOR DELETE
    TO authenticated
    USING (auth.uid() = user_id);


-- ============================================================================
-- 6. SEEDS (dados de exemplo opcionais)
-- ============================================================================
-- Descomente a seção abaixo para popular o banco com imóveis de exemplo.
-- Os IDs são simulados pois gen_random_uuid() gera valores dinâmicos.

-- INSERT INTO public.properties
--     (title, description, property_type, purpose, price, bedrooms, bathrooms,
--      area_sqm, location, neighborhood, city, state, image_url, featured)
-- VALUES
--     ('Casa Moderna com Piscina no Jardim Europa',
--      'Casa ampla em condomínio fechado, com 4 suítes, piscina aquecida e área gourmet.',
--      'Casa', 'comprar', 1250000.00, 4, 5, 420,
--      'Av. Europa, 1000 - Jardim Europa', 'Jardim Europa', 'São Paulo', 'SP',
--      'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&q=80', TRUE),
--
--     ('Apartamento Alto Padrão com Vista para o Mar',
--      'Apartamento de luxo com 3 suítes, varanda gourmet e vista panorâmica para o mar.',
--      'Apartamento', 'comprar', 980000.00, 3, 4, 180,
--      'Av. Orla, 500 - Orla da Praia', 'Orla da Praia', 'Santos', 'SP',
--      'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&q=80', TRUE),
--
--     ('Apartamento 2 Quartos com Varanda Encantadora',
--      'Apartamento aconchegante com 2 quartos, varanda e vaga de garagem.',
--      'Apartamento', 'alugar', 2800.00, 2, 2, 68,
--      'Rua dos Pinheiros, 300 - Pinheiros', 'Pinheiros', 'São Paulo', 'SP',
--      'https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800&q=80', FALSE);