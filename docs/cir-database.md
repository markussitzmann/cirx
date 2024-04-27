# CIR database

If the CIR system is (after build) available as images or running containers (after command ./up at the CIR root 
directory), the database is accessible by going to the CIR root directory and use 

    ./psql

It is important to use the command in this form, because the database is running in a Docker container and this 
scripts uses 'docker compose' under the hood.

The current default password is 'Arg0', however it can be changed in in the app.env directory (before a build, not)
well tested yet)

## Most important table

### cir_dataset

stores the available datasets or databases, respectively, for instance, PubChem or DTP/NCI. From here 
publisher can be reference (table _cir_publisher_). A dataset can be organized as dataset releases which is organized
in table _cir_dataset_release_. 

The table is unique by _name_ and _publisher_id_

### cir_dataset_release

contains the releases of a dataset or database, respectively. So for instance, 'PubChem Compound'
and 'PubChem Substance' can be considered as releases of the PubChem database and refer to the parent release (by column 
_parent_id_). Another example is the NCI/DTP database which has a release by PubChem or the NCI/CADD group, hence, a 
dataset release can have another publisher than the original, hence the table has a reference to table _cir_publisher_, 
too. 

The table is unique by _dataset_id_, _publisher_id_, _name_, _version_, _downloaded_ and _released_

### cir_structure_file_collection

Structure files (SDF or readable by CACTVS) in the 'CIR filestore' are organized in file collections. A file collection
adheres to a specific (column) _file_location_pattern_ inside the 'CIR filestore' and links any file matching this 
pattern to a specific dataset release (in table _cir_dataset_release_). However, a database can be also organized
by more than one file pattern which might advantageous later during file processing.

The table is unique by _release_id_ and _file_location_pattern_

### cir_structure_file

stores all files 


