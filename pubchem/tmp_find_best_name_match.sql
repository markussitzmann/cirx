
--- lowers the confidence of some PubChem Compound records
BEGIN;

SELECT count(*), count(distinct name_id) FROM cir_structure_name_associations a
    JOIN cir_pubchem_cid_structure s ON
        a.structure_id = s.structure_id
            and ficts_parent_id is null
            and name_type_id = 3;


COMMIT;

