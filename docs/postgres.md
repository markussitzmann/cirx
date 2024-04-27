





# Postgres Help Pages

Useful commands
===============

Table count fast estimate
-------------------------
``` sql
SELECT reltuples AS estimate FROM pg_class where relname = 'mytable';
``` 
from [Stack Overflow](https://stackoverflow.com/questions/7943233/fast-way-to-discover-the-row-count-of-a-table-in-postgresql)

Restore Database
-------------------------

``` sql
./pg_restore -c -d postgres /home/app/backup/default-0f008378fa8a-2024-02-08-001514.psql.bin
``` 