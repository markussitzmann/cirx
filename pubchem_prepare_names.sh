#!/bin/bash
set -e

source .env

docker-compose --f docker-compose.dev.yml run cirx python /home/app/pubchem/write_names.py


