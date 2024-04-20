

# Broken names

Same name with multiple structure
* select name_id,(select name from cir_structure_name where id=name_id), count(structure_id) from cir_structure_name_associations where affinity_class_id=1 group by name_id order by count desc limit 10000;

Pubchem CID with name
* select * from cir_pubchem_structure_name_cid c left join cir_structure_name n on c.name_id = n.id left join cir_pubchem_cid_parent p on p.cid = c.cid limit 10;

Structure file record to CID
* select structure_file_record_id, name as cid from cir_structure_file_record_names r left join cir_structure_name n on r.name_id = n.id where name_type_id=13 limit 10;

Linking cid to structure_file_record
* select * from cir_structure_file_record_names r left join cir_structure_name n on r.name_id = n.id left join cir_pubchem_structure_name_cid pn on n.name::int = pn.cid where name_type_id=13 limit 10;

Structure file record wit parent structure
* select * from cir_structure_file_record r left join cir_structure_parent_structure p on r.structure_id = p.structure_id limit 10;