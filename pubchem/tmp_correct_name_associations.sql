
--- lowers the confidence of some PubChem Compound records
BEGIN;

CREATE TABLE IF NOT EXISTS tmp_cir_structure_name_associations AS
SELECT * FROM cir_structure_name_associations WHERE name_id IN
(SELECT name_id FROM
    (SELECT name_id, count(structure_id) as scount
    FROM cir_structure_name_associations a
    WHERE affinity_class_id = 1
    GROUP BY name_id) AS ngroup
WHERE ngroup.scount > 1);

SELECT count(*) from tmp_cir_structure_name_associations;

--UPDATE cir_structure_name_associations set confidence=1 WHERE id IN (
-- SELECT count(aa.id) FROM
-- (SELECT * FROM cir_structure_name_associations WHERE name_id IN (
-- SELECT name_id FROM
--     (SELECT name_id, count(structure_id) as scount
--     FROM cir_structure_name_associations a
--     --WHERE name_type_id=5
--     GROUP BY name_id
--     ) AS ngroup
-- WHERE ngroup.scount > 1)
-- order by name_id) as aa limit 100;
-- --);

COMMIT;

