#!/bin/bash
set -e

source .env

docker-compose --f docker-compose.dev.yml run cirx python /home/app/pubchem/load_data_sources.py


