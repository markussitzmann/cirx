BEGIN;

-- 1 ***** update if from original build
--UPDATE cir_dataset_release SET downloaded='2023-11-01' WHERE id = 1;

-- insert **** PubChem Compound manually
-- INSERT INTO cir_dataset_release
-- VALUES (
--         1,
--         'PubChem Compound',
--         'PubChem Compound',
--         NULL, 'public', 'active', 0, NULL, '2023-11-01', now(), now(), 1, NULL, 4)
-- ON CONFLICT DO NOTHING;
--
-- 2 ***** insert PubChem Substance manually
-- INSERT INTO cir_dataset_release
-- VALUES (
--         2,
--         'PubChem Substance Projected',
--         'PubChem Substance records (SID) projected onto their corresponding CID record',
--         NULL, 'public', 'active', 0, NULL, '2023-11-01', now(), now(), 1, NULL, 4)
-- ON CONFLICT DO NOTHING;

-- 3 ***** insert PubChem SIDs into the name table
--INSERT into public.cir_structure_name(hash,name) SELECT md5(sid::text)::uuid,sid FROM cir_pubchem_sid_map
--ON CONFLICT DO NOTHING;


-- 4 ***** insert PubChem SIDs into the record tables (check if PubChem Compound is Release 1 and PubChem Substance Release 2
-- INSERT INTO cir_record(regid, version, added, modified, dataset_id, name_id, release_id, structure_file_record_id)
-- SELECT m.sid as regid,
--        1 as version,
--        now() as added, now() as modified, 1 as dataset_id,
--        (SELECT id from cir_structure_name as n where n.hash = md5(sid::text)::uuid) as name_id,
--        2 as release_id, structure_file_record_id
-- FROM cir_record r JOIN cir_pubchem_sid_map m ON r.regid::int=m.cid AND r.release_id=1 ORDER BY cid,source_id
-- ON CONFLICT DO NOTHING;

-- 5 **** insert PubChem SIDS into cir_record_names table
INSERT INTO cir_structure_file_record_names(name_id, name_type_id, structure_file_record_id)
SELECT name_id,
    12 as name_type_id,
    structure_file_record_id
FROM cir_record WHERE release_id=2;

-- 6 **** insert PubChem SIDS into cir_dataset table !!! Check if Publisher 4 is Pubchem, this is used for preliminary set uo
-- INSERT INTO cir_dataset(name, modified, added, publisher_id)
-- SELECT source_id as name, now(), now(), 4 FROM cir_pubchem_sid_map group by source_id
-- ON CONFLICT DO NOTHING;

-- 7 **** corrections from init stat
-- DELETE FROM cir_dataset where name = 'DTP/NCI' and publisher_id = 4;
-- DELETE FROM cir_dataset where name = 'ChEMBL' and publisher_id = 4;






COMMIT;

-- *** KEEP
-- SELECT name, description, NULL as description,
--        NULL as href, 'public' as class, 'active' as status, 0 as version, NULL as released,
--        2023-11-01 as downloaded, now() as added, now() as modified,
--        id as dataset_id,
--        1 as parent_id, 4 as publisher
-- FROM cir_dataset as d;

