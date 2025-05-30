CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS btree_gin;  -- For JSONB indexing 
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For trigram similarity