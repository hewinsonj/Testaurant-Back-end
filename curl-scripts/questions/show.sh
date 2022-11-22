#!/bin/bash

curl "http://localhost:8000/questions/${ID}/" \
  --include \
  --request GET \
  --header "Authorization: Token ${TOKEN}"

echo
