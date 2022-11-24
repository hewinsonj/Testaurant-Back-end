#!/bin/bash

curl "http://localhost:8000/test_manys/" \
  --include \
  --request GET \
  --header "Authorization: Token ${TOKEN}"

echo
