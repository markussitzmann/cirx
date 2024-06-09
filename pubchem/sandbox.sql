

BEGIN;

CREATE TABLE IF NOT EXISTS tmp_cir_structure_name_associations (LIKE cir_structure_name_associations INCLUDING all);

INSERT INTO tmp_cir_structure_name_associations(confidence, affinity_class_id, name_id, name_type_id, structure_id)
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
JOIN cir_structure_name n ON n.id = c.name_id
ON CONFLICT DO NOTHING;

-- WHERE name_id=4612;

-- WHERE c.cid = 1
-- ORDER BY c.cid ASC limit 10;
-- ON CONFLICT DO NOTHING;



-- SELECT emp_name,
-- CASE
-- WHEN AGE(current_date, emp_joining_date) < '1 year'
-- THEN 'Probation'
-- WHEN AGE(current_date, emp_joining_date) >=  '1 year' AND AGE(current_date, emp_joining_date) < '3 year'
-- THEN 'Contract'
-- WHEN AGE(current_date, emp_joining_date) >=  '3 year'
-- THEN 'Permanent'
-- END CASE
-- FROM emp_data
-- ORDER BY emp_id ASC;

COMMIT;