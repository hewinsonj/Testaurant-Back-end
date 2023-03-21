#!/bin/bash

ARE_MIGRATIONS_NEEDED=$(python manage.py showmigrations --list | grep '\[ \]' || :)

if [ ! "$ARE_MIGRATIONS_NEEDED" == "" ]; then
    echo ""
    echo "Migrations needed. Will apply shortly."
else
    echo ""
    echo "No migrations needed."
    echo "exiting."
    exit 0
fi

echo "Beginning migrations..."
python manage.py migrate
