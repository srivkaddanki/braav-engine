-- Migration: Enable pgvector and update embedding columns
-- Run this in Supabase SQL Editor (Dashboard > SQL Editor)

-- 1. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Alter thoughts table: convert embedding from JSONB to vector
ALTER TABLE thoughts 
DROP COLUMN IF EXISTS embedding,
ADD COLUMN embedding vector(384);

-- 3. Create HNSW index for fast similarity search on thoughts
CREATE INDEX thoughts_embedding_idx ON thoughts 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 4. Alter interactions table
ALTER TABLE interactions 
DROP COLUMN IF EXISTS embedding,
ADD COLUMN embedding vector(384);

-- 5. Create HNSW index for interactions
CREATE INDEX interactions_embedding_idx ON interactions 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 6. Alter files_in_void table
ALTER TABLE files_in_void 
DROP COLUMN IF EXISTS embedding,
ADD COLUMN embedding vector(384);

-- 7. Create HNSW index for files_in_void
CREATE INDEX files_in_void_embedding_idx ON files_in_void 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Done! Now embeddings are indexed for O(log n) search instead of O(n)
