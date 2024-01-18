#!/bin/bash
set -e

source .env

docker-compose run cirx python /home/app/pubchem/write_names.py


