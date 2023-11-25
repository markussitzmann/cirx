BEGIN;
CREATE TEMP TABLE tmp_structure_name
ON COMMIT DROP
AS
SELECT *
FROM cir_structure_name
WITH NO DATA;

COPY tmp_structure_name(hash,name) FROM '/home/app/pubchem/pubchem-names-hashed.txt';

INSERT INTO cir_structure_name(hash,name)
SELECT hash, name
FROM tmp_structure_name
ON CONFLICT DO NOTHING;
COMMIT;