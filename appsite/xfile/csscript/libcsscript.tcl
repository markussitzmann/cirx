proc file_ping {db user_file_id} {
	mysql::exec $db "update chemical_file.user_file set date_modified=now() where id=$user_file_id"
	return $user_file_id
}

proc fast_identifier_lookup {db user_file_id user_structure_id {push_to_db 1}} {

	if {$push_to_db} {
		set sql_cmd "replace into chemical_file.user_structure_identifier "
	} else {
		set sql_cmd ""
	}
	append sql_cmd "
		select 
			user_structure.id,
			(select lpad(conv(hashisy,10,16),16, '0') from chemical_structure.structure structure join chemical.compound compound on compound.structure_id = structure.id where compound.id=ficts_compound_id) as ficts,
			(select lpad(conv(hashisy,10,16),16, '0') from chemical_structure.structure structure join chemical.compound compound on compound.structure_id = structure.id where compound.id=ficus_compound_id) as ficus,
			(select lpad(conv(hashisy,10,16),16, '0') from chemical_structure.structure structure join chemical.compound compound on compound.structure_id = structure.id where compound.id=uuuuu_compound_id) as uuuuu,
			(select minimol from chemical_structure.structure structure join chemical.compound compound on compound.structure_id = structure.id where compound.id=ficts_compound_id) as ficts_parent_structure,
			(select minimol from chemical_structure.structure structure join chemical.compound compound on compound.structure_id = structure.id where compound.id=ficus_compound_id) as ficus_parent_structure,
			(select minimol from chemical_structure.structure structure join chemical.compound compound on compound.structure_id = structure.id where compound.id=uuuuu_compound_id) as uuuuu_parent_structure,
			1,
			0 
		from chemical_file_user_structure user_structure 
		join chemical.compound compound on user_structure.structure_id = compound.structure_id 
		join chemical.record_lookup_active_database lookup on lookup.ficts_compound_id = compound.id 
		join chemical_structure.structure structure on structure.id = user_structure.structure_id 
		where 
			user_file_id=$user_file_id and user_structure.id=$user_structure_id
		group by user_structure.structure_id"

	set result [::mysql::sel $db $sql_cmd -flatlist]

	return $result
}

proc fast_database_lookup {db user_file_id} {

	#(select f.id,r.id as rid,8 as association_type_id,database_id from chemical_file_user_structure f join chemical.compound c on c.structure_id = f.structure_id join chemical.record_lookup r on (r.uuuuu_compound_id =c.id) where user_file_id=1292) union (select f.id,r.id as rid,2 as association_type_id, database_id from chemical_file_user_structure f join chemical.compound c on c.structure_id = f.structure_id join chemical.record_lookup r on (r.ficus_compound_id =c.id) where user_file_id=1292) union (select f.id,r.id as rid,1 as association_type_id,database_id from chemical_file_user_structure f join chemical.compound c on c.structure_id = f.structure_id join chemical.record_lookup r on (r.ficts_compound_id =c.id) where user_file_id=1292) order by id,rid,association_type_id	
	
	set sql_cmd "insert ignore into chemical_file.user_structure_record"	
	append sql_cmd "
	(
		select 
			user_structure.id,
			lookup.id as record_id,
			database_id,
			release_id,
			8 as association_type_id
		from chemical_file.user_structure user_structure 
		join chemical.compound compound on compound.structure_id = user_structure.structure_id 
		join chemical.record_lookup lookup on (lookup.uuuuu_compound_id = compound.id) 
		where user_structure.user_file_id=$user_file_id and user_structure.structure_id != 1517
	) union (
		select 
			user_structure.id,
			lookup.id as record_id,
			database_id,
			release_id,
			2 as association_type_id
		from chemical_file.user_structure user_structure 
		join chemical.compound compound on compound.structure_id = user_structure.structure_id 
		join chemical.record_lookup lookup on (lookup.ficus_compound_id = compound.id) 
		where user_structure.user_file_id=$user_file_id and user_structure.structure_id != 1517
	) union (
		select
			user_structure.id,
			lookup.id as record_id,
			database_id,
			release_id,
			1 as association_type_id
		from chemical_file.user_structure user_structure
		join chemical.compound compound on compound.structure_id = user_structure.structure_id
		join chemical.record_lookup lookup on (lookup.ficts_compound_id = compound.id) 
		where user_structure.user_file_id=$user_file_id and user_structure.structure_id != 1517
	)
	"
	::mysql::exec $db $sql_cmd

	set sql_cmd "
		insert ignore into chemical_file.user_structure_database select user_structure_id,user_file_id,database_id,association_type_id 
		from chemical_file.user_structure_record r 
		join chemical_file.user_structure s on r.user_structure_id = s.id
		where user_file_id=$user_file_id
	"
	::mysql::exec $db $sql_cmd
#	set sql_cmd "insert ignore into chemical_file_user_structure_database"
#	append sql_cmd "
#	(
#		select 
#		user_structure.id,
#		user_file_id,
#		database_id,
#		1 
#	from chemical_file_user_structure user_structure 
#	join chemical.compound compound on user_structure.structure_id = compound.structure_id 
#	join chemical.record_lookup_active_database lookup on lookup.ficts_compound_id = compound.id 
#	where user_structure.user_file_id=$user_file_id and user_structure.structure_id != 1517 group by user_structure.id,database_id
#	) union (
#	select 
#		user_structure.id,
#		user_file_id,
#		database_id,
#		2 
#	from chemical_file_user_structure user_structure 
#	join chemical.compound compound on user_structure.structure_id = compound.structure_id 
#	join chemical.record_lookup_active_database lookup on (lookup.ficts_compound_id = compound.id or lookup.ficus_compound_id = compound.id)
#	where user_structure.user_file_id=$user_file_id and user_structure.structure_id != 1517 group by user_structure.id,database_id
#	) union (
#	select 
#		user_structure.id,
#		user_file_id,
#		database_id,
#		8 
#	from chemical_file_user_structure user_structure 
#	join chemical.compound compound on user_structure.structure_id = compound.structure_id 
#	join chemical.record_lookup_active_database lookup on (lookup.ficts_compound_id = compound.id or lookup.ficus_compound_id = compound.id or lookup.uuuuu_compound_id = compound.id) 
#	where user_structure.user_file_id=$user_file_id and user_structure.structure_id != 1517 group by user_structure.id,database_id
#	)"

	return
}

proc push_user_structure_inchi {db user_structure_id ehandle} {
	set dup [ens dup $ehandle]
	ens hadd $dup
	if {![catch {ens new $dup E_STDINCHI} inchi]} {
		set inchikey [ens new $dup E_STDINCHIKEY]
		mysql::exec $db "insert ignore into chemical_file.user_structure_inchi values($user_structure_id,'$inchikey','$inchi',1,0)"
	} else {
		mysql::exec $db "insert ignore into chemical_file.user_structure_inchi values($user_structure_id,NULL,NULL,0,1)"
	}
	ens delete $dup
}


# untested
proc push_user_structure {db user_structure_id ehandle} {
	set packstring [ens pack $ehandle]
	set hashisy [ens get $ehandle E_HASHISY]
	if {[info exists structure_hashisy_array($hashisy)]} {
		set structure_id $structure_hashisy_array($hashisy)
	} else {
		set structure_id NULL
	}
	mysql::exec $db "
		insert into chemical_file.user_structure(id, user_file_id, record, structure_id, hashisy, packstring, date_added, date_modified)
		values('', $user_file_id, $record, $structure_id, conv('$hashisy',16,10), '$packstring', now(), now())
	"
	#mysql::exec $db "
	#	insert into chemical_file.upload_user_structure(id, user_file_id, record, structure_id, hashisy, packstring, date_added, date_modified)
	#	values('', $user_file_id, $record, $structure_id, conv('$hashisy',16,10), '$packstring', now(), now())
	#"
	set user_structure_id [mysql::sel $db "
		select id from chemical_file.user_structure
		where user_file_id=$user_file_id and record=$record" -flatlist]
	return $user_structure_id
}

proc push_user_structure_images {db user_structure_id ens} {
	set ehandle [ens dup $ens]
	ens trim $ehandle
	set small NULL
	set medium NULL
	set large NULL
	set l [min 560 [max 280 [expr ([string length [ens get $ehandle E_SMILES]] * 15) / ([ens rings $ehandle {} count] + 1)]]] 
	#catch {
		catch {ens new $ehandle A_XY}
		set hashisy [ens get $ehandle E_HASHISY]
		foreach size {small medium large} dimensions [list {120 120} {265 220} "$l 280"] fontsize {5 8 10} linespacing {1 2 2} {
			prop setparam E_STRUCTURE_IMAGE_BASE64 width [lindex $dimensions 0]
			prop setparam E_STRUCTURE_IMAGE_BASE64 height [lindex $dimensions 1]
			prop setparam E_STRUCTURE_IMAGE_BASE64 linespacing $linespacing
			prop setparam E_STRUCTURE_IMAGE_BASE64 symbolfontsize $fontsize
			ens new $ehandle E_STRUCTURE_IMAGE_BASE64
			
			set $size [ens get $ehandle E_STRUCTURE_IMAGE_BASE64]
			
			#file_ping $db $user_file_id
		}
		set image_insert_clause "(conv('$hashisy',16,10), '$small', '$medium', '$large')"
		mysql::exec $db "
			insert ignore into chemical_file.user_structure_image(hashisy,small,medium,large)
			values $image_insert_clause
		"
		set image_id [mysql::sel $db "select id from chemical_file.user_structure_image where hashisy=conv('$hashisy',16,10)" -flatlist]
		# this update is needed because of a weird CACTVS bug
		mysql::exec $db "update chemical_file.user_structure set image_id=$image_id where id=$user_structure_id"
		mysql::exec $db "update chemical_file.upload_user_structure set image_id=$image_id where id=$user_structure_id"

	#}
	ens delete $ehandle
	return $image_id
}

proc normalize {db user_file_id do_identifier_lookup do_database_lookup} {
	
	file_ping $db $user_file_id

	set structure_list [mysql::sel $db "
		select id,record,packstring 
		from chemical_file.user_structure user_structure 
		left join chemical_file.user_structure_identifier identifier 
		on user_structure.id = identifier.user_structure_id 
		where user_file_id=$user_file_id and identifier.user_structure_id is null and user_structure.blocked=0
	" -list]

	array set ficts_ehandle_array {}
	set ficts_list {}
	foreach structure $structure_list {
		lassign $structure user_structure_id record packstring
		mysql::exec $db "update chemical_file.user_structure set blocked=1 where id=$user_structure_id"
		set ehandle [ens create $packstring]
		set ficts [lindex [split [ens get $ehandle E_FICTS_ID] "-"] 0]
		set ficts_ens [ens get $ehandle E_FICTS_STRUCTURE]
		ens trim $ficts_ens
		set ficts_packstring [ens pack $ficts_ens]
		set ficts_ehandle_array($user_structure_id) $ficts_ens
		set structure_id [::mysql::sel $db "select id from chemical_structure.structure where hashisy = conv('$ficts',16,10)" -flatlist]
		if {$structure_id != ""} {
			mysql::exec $db "update chemical_file.user_structure set 
				structure_id=$structure_id,
				hashisy='$ficts',
				packstring='$ficts_packstring',
				date_modified=now()
				where id=$user_structure_id
			"
		} else {
			mysql::exec $db "update chemical_file.user_structure set 
				structure_id=NULL,
				hashisy='$ficts',
				packstring='$ficts_packstring',
				date_modified=now()
				where id=$user_structure_id
			"
		}
		push_user_structure_inchi $db $user_structure_id $ficts_ens
		push_user_structure_images $db $user_structure_id $ficts_ens
		if {$do_identifier_lookup} {
			fast_identifier_lookup $db $user_file_id $user_structure_id
		}
		file_ping $db $user_file_id
		mysql::exec $db "update chemical_file.user_structure set blocked=0 where id=$user_structure_id"
	}
	if {$do_database_lookup} {
		fast_database_lookup $db $user_file_id
	}

	set structure_list [mysql::sel $db "
		select id,record,packstring 
		from chemical_file.user_structure user_structure 
		left join chemical_file.user_structure_identifier identifier 
		on user_structure.id = identifier.user_structure_id 
		where user_file_id=$user_file_id and identifier.user_structure_id is null and user_structure.blocked=0
	" -list]

	foreach structure $structure_list {
		lassign $structure user_structure_id record packstring
		set ehandle $ficts_ehandle_array($user_structure_id)
		set ficts [lindex [split [ens get $ehandle E_FICTS_ID] "-"] 0]
		set ficts_structure [ens get $ehandle E_FICTS_STRUCTURE]
		ens trim $ficts_structure
		file_ping $db $user_file_id
		set ficus [lindex [split [ens get $ehandle E_FICUS_ID] "-"] 0]
		set ficus_structure [ens get $ehandle E_FICUS_STRUCTURE]
		ens trim $ficus_structure
		file_ping $db $user_file_id
		set uuuuu [lindex [split [ens get $ehandle E_UUUUU_ID] "-"] 0]
		set uuuuu_structure [ens get $ehandle E_UUUUU_STRUCTURE]
		ens trim $uuuuu_structure
		file_ping $db $user_file_id
		#puts "$ficts $ficus $uuuuu $user_structure_id $record no"
		mysql::exec $db "
			replace into chemical_file.user_structure_identifier (user_structure_id,ficts_hashcode,ficus_hashcode,uuuuu_hashcode,ficts_parent_structure,ficus_parent_structure,uuuuu_parent_structure,valid,blocked)
			values($user_structure_id,'$ficts','$ficus','$uuuuu','$ficts_structure','$ficus_structure','$uuuuu_structure',1,0)
		"
	}
	return
}