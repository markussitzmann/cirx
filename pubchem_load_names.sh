#!/bin/bash
set -e

source .env

./psql -f /home/app/pubchem/load_names.sql

