# CIRx 

2022-2024 Rework of the CIR (Chemical Identifier Resolver)

## Requirements

Please have at least [Docker CE 20.10](<https://docs.docker.com/engine/installation/>) and 
[Docker Compose 1.29](<https://docs.docker.com/compose/install/>) installed on your system.
Installation of this packages also requires full installation and successful build of the Docker Cactvs package 
(see https://github.com/markussitzmann/docker-cactvs) 

## Installation

Clone the repository::

    git clone https://github.com/markussitzmann/cirx

Then, change into the newly created directory ::

    cd cirx/

and edit the central app.env file according to your needs. Most importanlty here are the settings of the
variables before starting any build:

    APP_HOME=/home/sitzmann/projects/cirx
    APP_UID=1000
    APP_GID=1000

Then run the following command (it is important that you do this from inside the `cirx` directory) ::

    ./build

This builds all image, starts the system and fills the database with some initial data. The CIR instance
should run then at 

    localhost:8000


The build script calls the falling scripts as subscripts

    ./docker-build
    ./django-init
    ./django-manage-py initdata

The first one of these scripts runs the build of all Docker images, the second one initializes the Django system
(database structure and Django setup), and the third script initializes the fresh system with some initial data in
the database.

### initdata command

The initdata command is run by the general Django management script manage.py, however, since CIR is running inside
a docker container, the wrapper script django-manage-py has been created for CIR.

The definition of the initdata process is available at following script
    
    appsite/etl/management/commands/initdata.py

inside the CIR root directory. It performs some exemplary data initialization processes in the CIR database.

A short version of the django-manage-py or Django manage.py command, respectively, is available as 

    ./cirx [management command], e.g. ./cirx initdata

### Other useful commands

Reset rebuilds the whole system (WARNING: all data in the database is lost)

    ./reset 

Cleans the database (WARNING: all data in the database is lost)

    ./cleardb

## Building the database

The CIR ETL process expects data in its so called _instore_, this can be a loose or organized collection of (SDF) files.
With a helper script _addfiles_ the files can be transfered to the CIR "filestore". The files in the "filestore" are
organized in a way the ETL processes needs and reads them, however, the files can also be directly organized in the
_filestore_ (under circumvention of the _instore_). 

The location of both file stores is set in the central _app.env_ configuration file:

APP_FILESTORE=/home/sitzmann/filestore
APP_INSTORE=/home/sitzmann/instore

### Addfiles command

If the process is started from the _instore_, some SDF files have to be put there and then the addfile command has to be 
used:

    ./cirx addfiles 
        --filepattern {the file filepattern of your SDF file starting from instore root} 
        --release 1 (this is is an example release created by the init process of the CIR build)
        --preprocessors 1 (unfortunately not so well defined yet, the initdata process specifies exemplary preprocessors
                           which are stored in table cir_structure_file_collection_preprocessor and  
                            cir_structure_file_collection_preprocessors) 

(Needs improvement: to add own releases, access the database from inside the cirx home directory the following way
it connects via docker to the database in the CIR postgres database in Docker image

    ./psql

and look for the table cir_dataset_release, see also database descriptions at [docs/postgres.md](docs/postgres.md))

Running the _addfile_ command will process all files matching the provided filepattern, i.e. they are chunked into
blocks of 10000 records, zipped, and organized as file collections in the _filestore_ directory of CIR. Additionally, 
some initial entries are added to database table _cir_structure_file_collection_ facilitating further processing. 
However, the _addfile_ command can be skipped and everything can be organized in the _filestore_ directory (this 
requires manual configuration of the _cir_structure_file_collection_ table).

### Register command

If all files have been organized as file collections (either by the addfile command or directly inside the instore and
database configuration, see above addfile command), the files can be registered running the command

    ./cirx register --file_collection_id  (or ./cirx register -c)

This starts counting the files in the filestore, reading the structures, adding them to the database 
(_cir_structure_ table) 




## Database Backups

The database backup process is based on the django dbbackup package.

The CIR database backups can be created by 

    ./cirx dbbackup

If no outputfile name is provided using the -o option, the database us dumped to the backup/ directory of the CIR
root directory. Nameing the dump file

    ./cirx dbbackup -o test.dump

writes the backup as test.dump to the backup directory.

In order to restore a database use

    ./cirx dbrestore

or use a specific dump with 

    ./cirx dbrestore -i some.dump

If no dump file name is provided, the most recent (generically named) dump file is used.



Markus Sitzmann
2024/01/14

