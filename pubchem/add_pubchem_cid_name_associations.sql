BEGIN;

-- INSERT INTO cir_structure_name_associations(confidence, affinity_class_id, name_id, name_type_id, structure_id)
-- SELECT 100 as confidence, 1 as affinity_class_id, name_id, 3 as name_type_id, structure_id
-- FROM cir_pubchem_structure_name_cid c
-- JOIN cir_structure_name n on n.id = c.name_id
-- JOIN cir_pubchem_cid_structure cs on c.cid = cs.cid
-- -- WHERE c.cid = 1
-- -- ORDER BY c.cid ASC limit 10;
-- ON CONFLICT DO NOTHING;

INSERT INTO cir_structure_name_associations(confidence, affinity_class_id, name_id, name_type_id, structure_id)
SELECT
    100 as confidence,
    1 as affinity_class_id,
    name_id,
    3 as name_type_id,
    CASE
        WHEN ficts_parent_id IS NOT NULL AND structure_id != ficts_parent_id THEN ficts_parent_id
        ELSE structure_id
    END as structure_id
FROM cir_pubchem_structure_name_cid c
JOIN cir_pubchem_cid_structure cs ON c.cid = cs.cid
ON CONFLICT DO NOTHING;

COMMIT;