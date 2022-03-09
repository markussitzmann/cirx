#!/bin/sh
#\
exec ${PATH}/tclcactvs -f "$0" ${1+"$@"}

lappend auto_path {*}$env(lib_paths)
package require mysqltcl

lappend cactvs(propertypath) {*}$env(lib_paths)

processor::init $env(logfile) $env(tracefile)

#smd4 alchemy gjf cerius sybyl sybyl2 cosmo sdf3000 table cml mopacout cif asn spc hyperchem tinker sln cdxml skc gaussout mopacin molconnz pdb cid xbsa png ole iff smarts bdb mopacin rosdal usmiles inchi mopacin cpacked mopacin compass gromacs maestro xfig tdt smd5 chai mrv sid gausscube gif xyzr cmf sharc smirks emf pcd vrml jcamp molgen bxml m3d jme xdf kcf pdbcode xtel scf swf xyz cas shelx ctx wln sk2 rtf 441 charmm stf car asnt tgf cdx chiron sddata vamp

filex load pdb
filex load sdf3000
filex load cerius
filex load hyperchem
filex load sln
filex load cdxml
filex load smirks
filex load ctx
filex load mrv
filex load maestro
filex load cif


prop setparam E_STDINCHIKEY prefix 0

lassign {*}$argv user_file_id event_id file_name structure_data max_records do_identifier_lookup do_database_lookup 


array set database [processor::get database]
set db [::mysql::connect -user $database(user) -password $database(password) -host $database(host) -db $database(name)]


# read all structures into ens handles
set record_count [::mysql::sel $db "select count(*) from chemical_file.user_structure where user_file_id=$user_file_id" -flatlist]
set field_list {}

set original_file_name [::mysql::sel $db "select name from chemical_file.user_file where id=$user_file_id" -flatlist]

if {$file_name != "None" && $structure_data == "None"} {
	
	set fhandle [molfile open $file_name]
	file_ping $db $user_file_id
	
	while {$record_count < $max_records} {
		if {[catch {molfile read $fhandle} ehandle]} {
			if {[molfile get $fhandle eof]} {break}
			set ehandle [ens create]
			lappend data_source_list "record [expr $record_count + 1] of file \"$original_file_name\" (read failed)"
			lappend read_error_list 1
		} else {
			lappend data_source_list "record [expr $record_count + 1] of file \"$original_file_name\""
			lappend read_error_list 0
		}
		lappend ehandle_list $ehandle
		set field_list [concat $field_list [molfile get $fhandle fields]]
		incr record_count
		file_ping $db $user_file_id
	}

} elseif {$file_name == "None" && $structure_data != "None"} {

	foreach {structure resolver_string} [split [decode -base64 $structure_data]] {
		if {[catch {ens create $structure} ehandle]} {
			set ehandle [ens create]
		}
		#ens set $ehandle E_CACTUS_DATA_SOURCE [decode -base64 $resolver_string]
		lappend ehandle_list $ehandle
		lappend data_source_list [decode -base64 $resolver_string]
		lappend read_error_list 0
		incr record_count
		file_ping $db $user_file_id
		if {$record_count == $max_records} {break}
	}

} else {
	error "upload error"	
}
mysql::exec $db "update chemical_file.user_file set records=$record_count where id=$user_file_id"

# find all fields in the original source file
set field_insert_clause {}
set fields {}

foreach field [lsort -unique $field_list] {
	set origname [regsub -all {\s} [prop get $field origname] {_}]
	set field_prop_array($origname) $field 
	#set origname [prop get $field origname]
	append field_insert_clause "($user_file_id,'$origname'),"
	lappend fields $origname
	file_ping $db $user_file_id
}
set field_insert_clause [string range $field_insert_clause 0 end-1]
if {[string length $field_insert_clause]} {
	mysql::exec $db "
		insert into chemical_file.user_file_field(user_file_id,original_name)
		values $field_insert_clause"
	array set field_array [::mysql::sel $db "
		select original_name,id 
		from chemical_file.user_file_field 
		where user_file_id=$user_file_id" -flatlist]
}
file_ping $db $user_file_id

set hashisy_list {}
foreach ehandle $ehandle_list {
	set dup [ens dup $ehandle]
	ens hadd $dup
	ens trim $dup
	#puts $processor::logfile [ens pack $ehandle]
	#flush $processor::logfile
	set hashisy [ens get $dup E_HASHISY]
	append hashisy_list " or hashisy=conv('$hashisy',16,10)"
	file_ping $db $user_file_id
	ens delete $dup
}
set where_clause [string range $hashisy_list 4 end]
array set structure_hashisy_array [::mysql::sel $db "
	select lpad(conv(hashisy,10,16),16, '0'),id from chemical_structure.structure where $where_clause
" -flatlist]

file_ping $db $user_file_id

# loop over all structures, create all images, read file fields etc.
set record [::mysql::sel $db "select max(record) from chemical_file.user_structure where user_file_id=$user_file_id" -flatlist]
if {$record == "{}"} {
	set record 1
} else {
	incr record
}

foreach ehandle $ehandle_list data_source $data_source_list read_error $read_error_list {
	set dup [ens dup $ehandle]
	ens trim $dup
	set packstring [ens pack $dup]
	set hashisy [ens get $dup E_HASHISY]
	if {[info exists structure_hashisy_array($hashisy)]} {
		set structure_id $structure_hashisy_array($hashisy)
	} else {
		set structure_id NULL
	}
	if {$event_id == "None"} {
		set event_id NULL
	}
	
	mysql::exec $db "
		insert into chemical_file.user_structure(id, user_file_id, event_id, image_id, record, structure_id, hashisy, packstring, date_added, date_modified, error, blocked)
		values('', $user_file_id, $event_id, NULL, $record, $structure_id, conv('$hashisy',16,10), '$packstring', now(), now(),$read_error,0)
	"
	#mysql::exec $db "
	#	insert into chemical_file.upload_user_structure(id, user_file_id, event_id, image_id, record, structure_id, hashisy, packstring, date_added, date_modified, error, blocked)
	#	values('', $user_file_id, $event_id, NULL, $record, $structure_id, conv('$hashisy',16,10), '$packstring', now(), now(),$read_error,0)
	#"

	set user_structure_id [mysql::sel $db "
		select id from chemical_file.user_structure
		where user_file_id=$user_file_id and record=$record" -flatlist]
	mysql::exec $db "
		insert into chemical_file.user_structure_data_source(user_structure_id, string)
		values($user_structure_id, '$data_source')
	"	

	push_user_structure_inchi $db $user_structure_id $ehandle
	
	# always do this at the end - some weird  bug
	push_user_structure_images $db $user_structure_id $ehandle
	
	# property loop
	set field_insert_clause {}
	foreach field $fields {
		#puts "$field [ens valid $ehandle $field]"
		set prop_name $field_prop_array($field)
		if {[ens valid $ehandle $prop_name]} {
			if {![catch {ens sqlget $ehandle $prop_name} field_value]} {
				set field_id $field_array($field)
				append field_insert_clause "($user_structure_id,$field_id,$field_value),"
			}
		}
	}
	set field_insert_clause [string range $field_insert_clause 0 end-1]
	if {[string length $field_insert_clause]} {
		mysql::exec $db "
			replace chemical_file.user_structure_field_value(user_structure_id,field_id,value)
			values $field_insert_clause
		"
	}
	file_ping $db $user_file_id
	
	if {$do_identifier_lookup} {
		fast_identifier_lookup $db $user_file_id $user_structure_id
	}
	file_ping $db $user_file_id

	incr record
	
}

if {$do_database_lookup} {
	fast_database_lookup $db $user_file_id
}
file_ping $db $user_file_id

molfile close all
::mysql::close $db

processor::shutdown
exit 1
