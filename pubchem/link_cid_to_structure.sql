BEGIN;

-- --INSERT INTO cir_pubchem_cid_structure(cid, structure_id, ficts_parent_id)
-- SELECT cid, p.structure_id, p.ficts_parent_id FROM cir_structure_file_record_names r
-- --SELECT * FROM cir_structure_file_record_names r
-- LEFT JOIN cir_structure_name n ON r.name_id = n.id
-- LEFT JOIN cir_pubchem_structure_name_cid pn ON n.name::int = pn.cid
-- LEFT JOIN cir_structure_file_record fr on r.structure_file_record_id = fr.id
-- LEFT JOIN cir_structure_parent_structure p on fr.structure_id = p.structure_id
-- WHERE name_type_id=13;
-- --ON CONFLICT DO NOTHING;

INSERT INTO cir_pubchem_cid_structure(cid, structure_id, ficts_parent_id)
SELECT cid, p.structure_id, p.ficts_parent_id FROM cir_pubchem_structure_name_cid pn
JOIN cir_structure_name n ON n.name::int = pn.cid
JOIN cir_structure_file_record_names r on n.id = r.name_id
JOIN cir_structure_file_record fr on r.structure_file_record_id = fr.id
JOIN cir_structure_parent_structure p on fr.structure_id = p.structure_id
WHERE name_type_id=13
ON CONFLICT DO NOTHING;

COMMIT;

