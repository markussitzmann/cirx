#!/bin/bash
set -e

source .env

#./psql -f /home/app/pubchem/create_pubchem_database_extensions.sql
./psql -f /home/app/pubchem/load_names.sql

