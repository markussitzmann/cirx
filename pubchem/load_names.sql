BEGIN;

-- CREATE TABLE IF NOT EXISTS cir_pubchem_structure_name_cid(
--     id bigserial PRIMARY KEY,
--     name_id bigint NOT NULL,
--     cid bigint NOT NULL,
--     UNIQUE(name_id, cid)
-- );

CREATE TEMP TABLE tmp_structure_name(
    id bigserial PRIMARY KEY,
    hash uuid NOT NULL,
    cid bigint NOT NULL,
    name text NOT NULL
)
ON COMMIT DROP;
-- AS
-- SELECT *
-- FROM cir_structure_name
-- WITH NO DATA;

COPY tmp_structure_name(hash,cid,name) FROM '/filestore/pubchem/pubchem-names-hashed.txt';

INSERT INTO cir_structure_name(hash,name)
SELECT hash::uuid, name
FROM tmp_structure_name
ON CONFLICT DO NOTHING;

INSERT INTO cir_pubchem_structure_name_cid(name_id, cid)
SELECT (select id from cir_structure_name as n where n.hash = t.hash), cid
FROM tmp_structure_name as t
ON CONFLICT DO NOTHING;

commit;

