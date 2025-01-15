#!/bin/bash

# PostgreSQL credentials
PG_USER="postgres"
PG_HOST="localhost"
PG_PORT="5432"
PG_PASSWORD=""  # Set this if your PostgreSQL user has a password

# SQLite root directory (recursive search)
SQLITE_DIR="$HOME/Downloads/dev_1"

# Find all SQLite files recursively
sqlite_files=$(find "$SQLITE_DIR" -type f -name "*.sqlite")

# Check if any SQLite files are found
if [[ -z "$sqlite_files" ]]; then
    echo "No SQLite files found in $SQLITE_DIR or its subdirectories."
    exit 1
fi

# Loop through all found SQLite files
for sqlite_file in $sqlite_files; do
    # Extract database name from the file path
    db_name=$(basename "$sqlite_file" .sqlite)

    echo "Dropping and recreating PostgreSQL database $db_name..."

    # Drop the PostgreSQL database if it exists
    PGPASSWORD="$PG_PASSWORD" psql -U "$PG_USER" -h "$PG_HOST" -p "$PG_PORT" -c "DROP DATABASE IF EXISTS \"$db_name\";" || {
        echo "Failed to drop database $db_name"; continue;
    }

    # Create the PostgreSQL database
    PGPASSWORD="$PG_PASSWORD" psql -U "$PG_USER" -h "$PG_HOST" -p "$PG_PORT" -c "CREATE DATABASE \"$db_name\";" || {
        echo "Failed to create database $db_name"; continue;
    }

    # Use pgloader to migrate
    echo "Migrating $sqlite_file to PostgreSQL database $db_name..."
    pgloader "$sqlite_file" postgresql://"$PG_USER"@"$PG_HOST":"$PG_PORT"/"$db_name" || {
        echo "Failed to migrate $sqlite_file to $db_name"; continue;
    }

    echo "Migration of $sqlite_file to $db_name completed."
done
