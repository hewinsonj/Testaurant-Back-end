#!/bin/bash

curl "http://localhost:8000/drinks/" \
  --include \
  --request GET \
  --header "Authorization: Token ${TOKEN}"

echo
