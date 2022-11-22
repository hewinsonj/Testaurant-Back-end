#!/bin/bash

curl "http://localhost:8000/questions/" \
  --include \
  --request GET \
  --header "Authorization: Token ${TOKEN}"

echo
