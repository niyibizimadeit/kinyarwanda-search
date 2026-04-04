-- ============================================================
-- Kinyarwanda-English Search Engine — Supabase Migration
-- ============================================================
-- Run this once in your Supabase SQL editor.
-- It never touches your existing columns or data.
-- Author : NIYIBIZI Prince
-- Project: kinyarwanda-search
-- ============================================================


-- ------------------------------------------------------------
-- STEP 1: Enable pgvector extension
-- ------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS vector;


-- ------------------------------------------------------------
-- STEP 2: Add 4 new columns to your existing products table
-- All columns are nullable — existing rows are unaffected.
-- ------------------------------------------------------------
ALTER TABLE products ADD COLUMN IF NOT EXISTS name_rw        TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS description_rw TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS search_text    TEXT;

-- 384-dimensional vector from paraphrase-multilingual-MiniLM-L12-v2
ALTER TABLE products ADD COLUMN IF NOT EXISTS embedding      VECTOR(384);


-- ------------------------------------------------------------
-- STEP 3: Create index for fast vector similarity search
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS products_embedding_idx
  ON products
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);


-- ------------------------------------------------------------
-- STEP 4: Create the search_products RPC function
-- This is the single function your Next.js app calls.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION search_products(
  query_embedding  VECTOR(384),
  query_text       TEXT,
  match_count      INT DEFAULT 10
)
RETURNS TABLE (
  id              UUID,
  name            TEXT,
  name_rw         TEXT,
  description     TEXT,
  description_rw  TEXT,
  category        TEXT,
  price           NUMERIC,
  old_price       NUMERIC,
  badge           TEXT,
  has_variations  BOOLEAN,
  stock           INT,
  image_url       TEXT,
  similarity      FLOAT
)
LANGUAGE SQL STABLE
AS $$
  SELECT
    p.id,
    p.name,
    p.name_rw,
    p.description,
    p.description_rw,
    p.category,
    p.price,
    p.old_price,
    p.badge,
    p.has_variations,
    p.stock,
    p.image_url,
    1 - (p.embedding <=> query_embedding) AS similarity
  FROM products p
  WHERE
    p.is_active = TRUE
    AND p.embedding IS NOT NULL
  ORDER BY p.embedding <=> query_embedding
  LIMIT match_count;
$$;


-- ------------------------------------------------------------
-- STEP 5: Verify all columns exist
-- ------------------------------------------------------------
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'products'
ORDER BY ordinal_position;