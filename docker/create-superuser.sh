#!/bin/bash

docker-compose run \
--rm \
-e DJANGO_SUPERUSER_EMAIL="guy@gmail.com" \
-e DJANGO_SUPERUSER_PASSWORD="pop" \
testaurant_api \
bash -c \
"
  python manage.py createsuperuser --noinput
"