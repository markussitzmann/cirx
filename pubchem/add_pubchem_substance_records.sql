BEGIN;

-- ***** update if from original build
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
-- ***** insert PubChem Substance manually
-- INSERT INTO cir_dataset_release
-- VALUES (
--         2,
--         'PubChem Substance Projected',
--         'PubChem Substance records (SID) projected onto their corresponding CID record',
--         NULL, 'public', 'active', 0, NULL, '2023-11-01', now(), now(), 1, NULL, 4)
-- ON CONFLICT DO NOTHING;

-- ***** insert PubChem SIDs into the name table
--INSERT into public.cir_structure_name(hash,name) SELECT md5(sid::text)::uuid,sid FROM cir_pubchem_sid_map
--ON CONFLICT DO NOTHING;


-- ***** insert PubChem SIDs into the record tables (check if PubChem Compound is Release 1 and PubChem Substance Release 2
-- INSERT INTO cir_record(regid, version, added, modified, dataset_id, name_id, release_id, structure_file_record_id)
-- SELECT m.sid as regid,
--        1 as version,
--        now() as added, now() as modified, 1 as dataset_id,
--        (SELECT id from cir_structure_name as n where n.hash = md5(sid::text)::uuid) as name_id,
--        2 as release_id, structure_file_record_id
-- FROM cir_record r JOIN cir_pubchem_sid_map m ON r.regid::int=m.cid AND r.release_id=1 ORDER BY cid,source_id
-- ON CONFLICT DO NOTHING;

INSERT INTO cir_structure_file_record_names(name_id, name_type_id, structure_file_record_id)
SELECT name_id,
    12 as name_type_id,
    structure_file_record_id
FROM cir_record WHERE release_id=2;

COMMIT;

