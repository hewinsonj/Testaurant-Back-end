#!/bin/bash

curl "http://localhost:8000/tests/" \
  --include \
  --request GET \
  --header "Authorization: Token ${TOKEN}"

echo
