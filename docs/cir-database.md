# CIR database

[This document contains the most important tables necessary for running CIR, other tables are for future extensions]

If the CIR system is (after build) available as images or running containers (after command ./up at the CIR root 
directory), the database is accessible by going to the CIR root directory and use the command

    ./psql

It is important to use the command in this form (from the CIR root directory), because the database is running in a 
Docker container and this scripts uses 'docker compose' under the hood.

The current default password is 'Arg0', however it can be changed in the app.env directory (before a build, not)
well tested yet)

## Most important table

### cir_dataset

stores the available datasets or databases, respectively, for instance, PubChem or DTP/NCI. From here 
publisher can be reference (table _cir_publisher_). A dataset can be organized as dataset releases which is organized
in table _cir_dataset_release_. 

The table is unique by column _name_ and _publisher_id_.

### cir_dataset_release

contains the releases of a dataset or database, respectively. So for instance, 'PubChem Compound'
and 'PubChem Substance' can be considered as releases of the PubChem database and refer to the parent release (by column 
_parent_id_). Another example is the NCI/DTP database which has a release by PubChem or the NCI/CADD group, hence, a 
dataset release can have another publisher than the original dataset. For that this table provides a reference to table 
_cir_publisher_ like table _cir_dataset_, too. 

The table is unique by columns _dataset_id_, _publisher_id_, _name_, _version_, _downloaded_ and _released_.

### cir_structure_file_collection

Structure files (SDF or readable by CACTVS) in the 'CIR filestore' are organized in file collections. The files 
belonging to a file collection have to adhere to a specific file name pattern which is stored in (column) 
_file_location_pattern_. The file name patterns are created or have to be configured relative to the configured
'CIR filestore' root. A file collection is then linked to a specific dataset release (in table _cir_dataset_release_)
by column _release_id_. Alternatively, a (very large) database can be also organized by more than one file pattern 
which might advantageous later during file processing.

The table is unique by columns _release_id_ and _file_location_pattern_.

### cir_structure_file

This table contains every structure file registered to the 'CIR filestore' and links it to the file collection it
belongs to. The file  name is referenced starting from the /filestore root mounting point inside the DOCKER container 
(usually /filestore), which can be mounted to a directory outside the container (see app.env). During the (regular) 
file registering process structure files are chunked up into blocks of 10000 records and packed (see also
[README.md](../README.md)).

The table is unique by columns _collection_id and _file_

### cir_record

This table uniquely references every file record available from any structure files. Most importantly it stores the 
REGID and the name_id of the REGID (referring to the corresponding name entry at table _cir_structure_name_). 
It also links a record to its dataset and release as well as its structure_file_record. The table can be used to 
references more than one version of the same structure file record. This file is filled during the file register 
process (see also [README.md](../README.md)).

The table is unique by columns _name_id_, _version_ and _release_id_.

### cir_structure

This table stores all available structures as CACTVS minimols unique by CACTVS E_HASHISY. The CACTVS hash values have 
been shifted from 64-bit unsigned to 64-bit signed (because Postgres supports only this int datatype). The table 
contains all original file record structures which have been added during the file registration 
process and additionally all (new) structures which have been created during structure normalization process 
(see table _cir_structure_parent_structure_).

This table is unique by column _hash_.

### cir_structure_parent_structure

This table creates a link between a structure from table _cir_structure_ and its NCI/CADD parent structure (FICTS, 
FICuS, uuuuu). If a _structure_id_ refers to itself, it is a parent structure and registered as compound (see table 
_cir_compound_). NULL values for higher order parent structure (FICTS or FICuS) means, the structure is also a either
a FICuS parent structure in itself (FICTS is NULL) or a uuuuu parent structure (FICTS and uuuuu are NULL).

The table is unique by column _structure_id_.

### cir_compound

Whenever a structure has been the result of NCI/CADD parent structure calculation or normalization, respectively, it is
registered as a compound, hence its structure_id is assigned a compound ID in this table.

The table is unique by column _id_.

### cir_structure_name

The table contains all names and REGIDs collected during file record registration process. Each name string is MD5 
hashed and cast into the Postgres type UUID which is used as the name hash.

The table is unique by column _hash_.

### cir_structure_name_associations

This table creates all associations between an entry of table _cir_structure_ and _cir_structure_name_. It also includes
a confidence level (currently by default 100 for most entries), the affinity class (these are created from whether the 
association has been found via FICTS, FICuS or uuuuu parent structure, see also table _cir_name_affinity_class_), and 
the _name_type_id_.

The table is unique by columns _name_id, _structure_id_, _name_type_id_, amd _affinity_class_id_)

### cir_name_type

This table references all name types used in table _cir_structure_name_associations_. 

The table is unique by column _title_.

### cir_name_affinity_class

The classes listed in this table are used in table _cir_structure_name_association_ for describing how closely a 
name association links a nme to a structure. These values are set during the linkname process when registering structures
to the database, for instance, if a name is linked on basis of FICTS parent structure, the name affinity class is 
set to 'exact'.

The table is unique by column _title_.

### cir_inchi

This table stores all InChIs calculated for the structures in table _cir_structure_. Each entry contains the 
InChI string, the InChI key in full length, the InChI key blockwise in columns and the version string. The table also 
contains a hash of the InChIKey which is the MD5 value of the InChIKey cast into the UUID data type of Postgres. The
hash has been used for calculating uniqueness.

The table is unique by column _hash_.

### cir_structure_inchi_associations

This table creates the associtions between the structures available in table _cir_structure_ and their calculated
InChIs in table _cir_inchi_. The association also includes the software version of the InChI library, the applied 
save_opts (except for Standard InChI) as well as the InChI Type used for the calculation (see next table).

This table is unique by columns _structure_id_, _inchi_id, _inchi_type_id_ and _save_opts_. 

### cir_inchi_type

This table stores the available InChI types 



