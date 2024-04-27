

# Broken names

Same name with multiple structure
*  

Pubchem CID with name
* select * from cir_pubchem_structure_name_cid c left join cir_structure_name n on c.name_id = n.id left join cir_pubchem_cid_parent p on p.cid = c.cid limit 10;

Structure file record to CID
* select structure_file_record_id, name as cid from cir_structure_file_record_names r left join cir_structure_name n on r.name_id = n.id where name_type_id=13 limit 10;

Linking cid to structure_file_record
* select * from cir_structure_file_record_names r left join cir_structure_name n on r.name_id = n.id left join cir_pubchem_structure_name_cid pn on n.name::int = pn.cid where name_type_id=13 limit 10;

Structure file record wit parent structure
* select * from cir_structure_file_record r left join cir_structure_parent_structure p on r.structure_id = p.structure_id limit 10;

single broken name
* select * from cir_structure_name_associations a left join cir_pubchem_cid_structure c on a.structure_id = c.structure_id where name_id=229;

counting broken names
* select count(*) from (select name_id, count(*) from cir_structure_name_associations where confidence = 1 group by name_id) as n where n.count 