BEGIN;

CREATE TABLE IF NOT EXISTS cir_pubchem_structure_name_cid(
    id bigserial PRIMARY KEY,
    name_id bigint NOT NULL,
    cid bigint NOT NULL,
    UNIQUE(name_id, cid)
);

CREATE TABLE if not EXISTS cir_pubchem_sid_map(
    id bigserial PRIMARY KEY,
    sid bigint NOT NULL,
    cid bigint DEFAULT NULL,
    source_id TEXT,
    regid TEXT,
    UNIQUE(sid, cid)
);

COMMIT;



