#!/bin/bash

curl "http://localhost:8000/results/${ID}/" \
  --include \
  --request GET \
  --header "Authorization: Token ${TOKEN}"

echo
