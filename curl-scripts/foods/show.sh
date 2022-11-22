#!/bin/bash

curl "http://localhost:8000/foods/${ID}/" \
  --include \
  --request GET \
  --header "Authorization: Token ${TOKEN}"

echo
