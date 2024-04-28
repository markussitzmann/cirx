# CIR database

[This document contains the most important tables necessary for running CIR, other tables are for future extensions]

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

This table contains every structure file available at the filestore and links it to a file collection. The file name is 
referenced starting from the /filestore root mounting point inside the DOCKER container (usually /filestore), which can 
be mounted to a directory outside the container (see app.env). During the (regular) file registering process structure 
files are chunked up into blocks of 10000 records and packed.

The table is unique by _collection_id and _file_

### cir_record

This table stores uniquely every record available from a structure file. Most importantly it stores the REGID and the
name_id (referring to table _cir_structure_name_ of the regid). It also links a record to its dataset and release as
well as its structure_file_record. The table can be used to references more than one version of the same structure
file record. This file is filled during the file register process.

The table is unique by _name_id_, _version_ and _release_id_.

### cir_structure

This table stores all available structures as CACTVS minimols unique by CACTVS E_HASHISY. Because this is a
Postgres database the CACTVS hash value has been shifted from 64-bit unsigned to 64-bit signed. The table contains
all original file record structures which are added during the file registration process and also all structures
which are created during structure normalization process (see table _cir_structure_parent_structure_).

This table is unique by _hash_.

### cir_structure_parent_structure

This table creates a link between a structure from table _cir_structure_ and its NCI/CADD parent structure (FICTS, 
FICuS, uuuuu). If a _structure_id_ refers to itself, it is a parent structure and registered as compound (see table 
_cir_compound_). NULL values for higher order parent structure (FICTS or FICuS) means, the structure is also a either
a FICuS parent structure in itself (FICTS is NULL) pr a uuuuu parent structure (FICTS and uuuuu are NULL).

The table is unique by _structure_id_.

### cir_compound

Whenever a structure has been the result of NCI/CADD parent structure calculation or normalization, respectively, it is
registered as a compound, hence its structure_id is assigned a compund ID in this table.

The table is unique by _id_.

### cir_structure_name

The table contains all names and REGIDs collected during file record registration process. Each name string is MD5 
hashed and casted into the Postgres type UUID which is used as the name hash.

The table is unique by _hash_.

### cir_structure_name_associations

This table creates all associations between an entry of table _cir_structure_ and _cir_structure_name_. It also includes
a confidence level (currently by default 100), the affinity class (these are created from whether the association has
been found via FICTS, FICuS or uuuuu parent structure), and the _name_type_id_.

The table is unique by _name_id, _structure_id_, _name_type_id_, amd _affinity_class_id_)

### cir_name_type



The table is unique by _title_