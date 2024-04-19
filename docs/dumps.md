# List of database dumps

* full-2024-04-11: contains PubChem SIDs merged into cir_records and cir_record_names

# List of Backups

* pubchem-sid-records-added.psql.bin contains the full build with PubChem SIDS merged into cir_structure_names


# Broken names

* select name_id,(select name from cir_structure_name where id=name_id), count(structure_id) from cir_structure_name_associations where affinity_class_id=1 group by name_id order by count desc limit 10000;
