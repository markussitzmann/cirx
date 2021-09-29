#!/bin/sh
mysqldump -u root -pArg0 -h 129.43.27.122 chemical_file --no-data \
upload_user_structure \
upload_user_structure_field_value \
upload_user_structure_image \
user_file \
user_file_field \
user_file_key \
user_file_status \
user_structure \
user_structure_database \
user_structure_field_value \
user_structure_identifier \
user_structure_image \
user_structure_inchi \
user_structure_data_source \
user_file_event \
> chemical_file.sql

mysql -u djangoroot -h 129.43.27.140 -pdjangoDJANGO chemical_file < ./chemical_file.sql
