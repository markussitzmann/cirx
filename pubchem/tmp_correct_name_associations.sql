
--- lowers the confidence of some PubChem Compound records
BEGIN;

CREATE TABLE IF NOT EXISTS tmp_cir_structure_name_associations AS
SELECT * FROM cir_structure_name_associations WHERE affinity_class_id = 1 and name_id IN
(SELECT name_id FROM
    (SELECT name_id, count(structure_id) as scount
    FROM cir_structure_name_associations a
    WHERE affinity_class_id = 1
    GROUP BY name_id) AS ngroup
WHERE ngroup.scount > 1);


-- UPDATE tmp_cir_structure_name_associations as m SET confidence = o.confidence FROM
-- (SELECT i.name_id, ceil(100/i.c) as confidence FROM
--     (SELECT name_id, count(*) as c FROM tmp_cir_structure_name_associations group by name_id) as i
-- ) as o
-- WHERE o.name_id = m.name_id;

CREATE TABLE IF NOT EXISTS tmp_best_cir_structure_name_associations AS
SELECT a.* FROM cir_structure_name_associations a
    JOIN cir_pubchem_cid_structure s ON
        a.structure_id = s.structure_id
            and ficts_parent_id is null
            and name_type_id = 3;

COMMIT;

