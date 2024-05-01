
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

--SELECT count(*) from tmp_cir_structure_name_associations;

--CREATE TABLE IF NOT EXISTS tmp_cir_new_confidence AS
-- SELECT a.id, ceil(100/(SELECT count(*) as ncount FROM tmp_cir_structure_name_associations i where i.name_id = a.name_id)) as i
-- FROM tmp_cir_structure_name_associations a WHERE name_id=229;
UPDATE tmp_cir_structure_name_associations as m SET confidence = o.confidence FROM
(SELECT i.name_id, ceil(100/i.c) as confidence FROM
    (SELECT name_id, count(*) as c FROM tmp_cir_structure_name_associations group by name_id) as i
) as o
WHERE o.name_id = m.name_id;

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

