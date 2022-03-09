#!/bin/sh
#\
exec ${PATH}/tclcactvs -f "$0" ${1+"$@"}

lappend auto_path {*}$env(lib_paths)
package require mysqltcl

lappend cactvs(propertypath) {*}$env(lib_paths)

processor::init $env(logfile) $env(tracefile)
ens::identifier::create

#puts $processor::logfile $cactvs(propertypath)

filex load pdb
filex load cdx

ens::identifier::create

prop setparam E_STDINCHIKEY prefix 0

prop create E_CACTUS_DATA_SOURCE datatype string origname cactus_data_source

#lassign $argv user_file_id
lassign {*}$argv user_file_id do_identifier_lookup do_database_lookup

array set database [processor::get database]
set db [::mysql::connect -user $database(user) -password $database(password) -host $database(host) -db $database(name)]

normalize $db $user_file_id $do_identifier_lookup $do_database_lookup

file_ping $db $user_file_id

molfile close all
::mysql::close $db

processor::shutdown
exit 1
