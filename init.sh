#!/bin/sh
echo "SELECT 'CREATE DATABASE pollsdb' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'pollsdb')\gexec" | psql