#!/bin/bash

# PostgreSQL credentials
PG_USER="postgres"
PG_HOST="localhost"

# Directory containing SQLite databases (use an absolute path)
SQLITE_DIR="$HOME/Downloads/dev_1/dev_20240627/dev_databases/dev_databases"

# Loop through each SQLite file in the directory
for sqlite_file in "$SQLITE_DIR"/*/*.sqlite; do
    # Check if the file exists (in case there are no matches)
    if [[ ! -f "$sqlite_file" ]]; then
        echo "No SQLite files found in $SQLITE_DIR. Skipping..."
        continue
    fi

    # Extract database name
    db_name=$(basename "$sqlite_file" .sqlite)

    echo "Migrating $sqlite_file to PostgreSQL database $db_name..."

    # Create the PostgreSQL database
    PGPASSWORD="" psql -U "$PG_USER" -h "$PG_HOST" -c "CREATE DATABASE \"$db_name\";" || {
        echo "Failed to create database $db_name"; continue;
    }

    # Use pgloader to migrate
    pgloader "$sqlite_file" postgresql://"$PG_USER"@"$PG_HOST"/"$db_name" || {
        echo "Failed to migrate $sqlite_file to $db_name"; continue;
    }

    echo "Migration of $sqlite_file to $db_name completed."
done

