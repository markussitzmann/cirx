#!/bin/sh
#\
exec ${PATH}/tclcactvs -f "$0" ${1+"$@"}

lappend auto_path {*}$env(lib_paths)
package require mysqltcl

lappend cactvs(propertypath) {*}$env(lib_paths)

processor::init $env(logfile) $env(tracefile)

array set database [processor::get database]
set db [::mysql::connect -user $database(user) -password $database(password) -host $database(host) -db $database(name)]

set calculate_3d [processor::get calculate_3d]
set only_records [split [processor::get only_records] ,]
if {$only_records=="None"} {set only_records {}}

#puts $processor::logfile $only_records

lassign {*}$argv user_file_id download_file_name download_format

file_ping $db $user_file_id

set user_file_data [::mysql::sel $db "select id,name from chemical_file.user_file where id=$user_file_id" -flatlist]
lassign $user_file_data dummy user_file_name

set outfile [molfile open $download_file_name w]

set only_record_where_clause {}
foreach only_record $only_records {
	append only_record_where_clause " OR record=$only_record"
}
set only_record_where_clause [string range $only_record_where_clause 4 end]

if {[string length $only_record_where_clause]} {
	set record_list [mysql::sel $db "
		select id,record,packstring from chemical_file.user_structure where user_file_id=$user_file_id and ($only_record_where_clause) order by record
	" -list]
} else {
	set record_list [mysql::sel $db "
		select id,record,packstring from chemical_file.user_structure where user_file_id=$user_file_id order by record
	" -list]
}

set field_list [::mysql::sel $db "
	select original_name from chemical_file.user_file_field
	where user_file_id=$user_file_id
" -flatlist]
#array set field_list_array [::mysql::sel $db "select id, original_name from chemical_file_user_file_field" -flatlist]

set structure_id_or_list [string range [concat {*}[mysql::sel $db "
	select concat('user_structure_id=', id, ' OR') from chemical_file.user_structure where user_file_id=$user_file_id
" -flatlist]] 0 end-3]

if {[string length $structure_id_or_list]} {
	set structure_field_value_list [mysql::sel $db "
		select user_structure_id, original_name, value from chemical_file.user_structure_field_value 
		join chemical_file.user_file_field on chemical_file.user_file_field.id = chemical_file.user_structure_field_value.field_id
		where $structure_id_or_list
	" -list]
} else {
	set structure_field_value_list {}
}

#set structure_field_value_array {} 
foreach structure_field_value $structure_field_value_list {
	lassign $structure_field_value structure_id field value
	if {[info exists structure_field_value_array($structure_id)]} {
		lappend structure_field_value_array($structure_id) $field $value
	} else {
		set structure_field_value_array($structure_id) $field 
		lappend structure_field_value_array($structure_id) $value
	}
}
#parray structure_field_value_array

foreach field $field_list {
	prop create [string toupper E_$field] origname $field datatype stringvector
}
molfile set $outfile writelist $field_list

#set calculate_3d 0
set ehandle_list {}
foreach record $record_list {
	lassign $record user_structure_id record_number packstring
	set ehandle [ens create $packstring]
	#if {$calculate_3d} {
	#	if {[catch {ens get $ehandle A_XYZ}]} {
	#		molfile set $outfile writeflags write2d
	#	} else {
	#		molfile set $outfile writeflags write3d
	#	}
	#}
	if [info exists structure_field_value_array($user_structure_id)] {
		foreach {field_name field_value} $structure_field_value_array($user_structure_id) {
			#puts $processor::logfile "$field_name $field_value"
			#flush $processor::logfile
			catch {
			ens set $ehandle [string toupper E_$field_name] \"$field_value\"
			}
		}
	}
	file_ping $db $user_file_id
	molfile write $outfile $ehandle
	ens delete $ehandle
}

molfile close all
::mysql::close $db

processor::shutdown
exit 1