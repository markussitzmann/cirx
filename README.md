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

## Building the database

The CIR ETL process expects data in its so called "instore", this can be a loose or organized collection of (SDF) files.
With a helper script "addfiles" the files can be transfered to the CIR "filestore". The files in the "filestore" are
organized in a way the ETL processes needs and reads them, however, the files can also be directly organized in the
"filestore" (under circumvention of the "instore"). 

The location of both file stores is set in the central app.env configuration file:

APP_FILESTORE=/home/sitzmann/filestore
APP_INSTORE=/home/sitzmann/instore

If you start from addstore, put some SDF files there and do

    ./cirx addfiles 
        --filepattern {the file filepattern of your SDF file starting from instore root} 
        --release 1 (this is is an example release created by the init process)

(Needs improvement: to add own releases, access the database from inside the cirx home directory the following way
it connects via docker to the database in the CIR postgres database in Docker image

    ./psql

and look for the table cir_dataset_release)

Running the "addfile" command will process all files matching the provided filepattern, count their size, chunk them
in blocks and will store packed SDF blocks in the /filestore directory. It will also create the necessary entries in
the cir_structure_file_collection table which are needed for the further processing (if you want to skip the "instore"
and organize your files directly in "filestore", you have to fill in the entries into this table manually).

IF the addfile process is finished, your original files are organized as file cellections in the "filestore".

Next step is registering all file records, i.e. the existence of the record, its ID, is structure, names  





Markus Sitzmann
2024/01/14

