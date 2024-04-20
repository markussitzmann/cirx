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

CREATE TABLE IF NOT EXISTS cir_pubchem_cid_parent(
    id bigserial PRIMARY KEY,
    cid bigint NOT NULL,
    cid_parent bigint NOT NULL,
    UNIQUE(cid, cid_parent)
);

CREATE TABLE IF NOT EXISTS cir_pubchem_cid_structure(
    id bigserial PRIMARY KEY,
    cid bigint NOT NULL,
    structure_id bigint NOT NULL,
    ficts_parent_id bigint,
    UNIQUE(cid, structure_id)
);

COMMIT;



