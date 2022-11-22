#!/bin/bash

curl "http://localhost:8000/drinks/${ID}/" \
  --include \
  --request GET \
  --header "Authorization: Token ${TOKEN}"

echo
