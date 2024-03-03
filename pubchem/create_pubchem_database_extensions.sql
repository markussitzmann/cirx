BEGIN;

CREATE TABLE IF NOT EXISTS cir_pubchem_structure_name_cid(
    id bigserial PRIMARY KEY,
    name_id bigint NOT NULL,
    cid bigint NOT NULL,
    UNIQUE(name_id, cid)
);

COMMIT;



