-- 全唐诗检索 MVP — PostgreSQL 初始化
-- 由 docker-entrypoint-initdb.d 或 tools/sync_postgres.py 使用

CREATE TABLE IF NOT EXISTS poems (
    id              TEXT PRIMARY KEY,
    source_file     TEXT NOT NULL,
    juan_ming       TEXT,
    pian_ti         TEXT,
    zuo_zhe         TEXT,
    zheng_wen       TEXT,
    ticai_da        TEXT,
    ticai_xiao      TEXT,
    kuohao_nei      TEXT,
    parse_note      TEXT,
    synced_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_poems_juan ON poems (juan_ming);
CREATE INDEX IF NOT EXISTS idx_poems_zuo_zhe ON poems (zuo_zhe);
CREATE INDEX IF NOT EXISTS idx_poems_ticai_da ON poems (ticai_da);
CREATE INDEX IF NOT EXISTS idx_poems_source ON poems (source_file);

-- 语义 enrichment（阶段 B 使用）
CREATE TABLE IF NOT EXISTS poem_enrichment (
    poem_id         TEXT PRIMARY KEY REFERENCES poems (id) ON DELETE CASCADE,
    summary         TEXT,
    enrich_source   TEXT,
    enrich_status   TEXT NOT NULL DEFAULT 'draft',
    enrich_note     TEXT,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_log (
    id              BIGSERIAL PRIMARY KEY,
    entity_type     TEXT NOT NULL,
    entity_id       TEXT NOT NULL,
    action          TEXT NOT NULL,
    actor           TEXT,
    payload         JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
