BEGIN;

COPY cir_pubchem_cid_parent(cid, cid_parent) FROM '/filestore/pubchem/cid-parent-prepared.txt' NULL '';

-- INSERT INTO cir_structure_name(hash,name)
-- SELECT hash::uuid, name
-- FROM tmp_structure_name
-- ON CONFLICT DO NOTHING;
--
-- INSERT INTO cir_pubchem_structure_name_cid(name_id, cid)
-- SELECT (select id from cir_structure_name as n where n.hash = t.hash), cid
-- FROM tmp_structure_name as t
-- ON CONFLICT DO NOTHING;

COMMIT;
