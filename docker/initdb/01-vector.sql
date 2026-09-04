-- Refs: P0-compose D4 D5 S3.1
-- pgvector 확장을 최초 기동 시 생성한다. person_aliases.embedding vector(1536) (S3.1, D4)의 전제 조건.
CREATE EXTENSION IF NOT EXISTS vector;
