#!/bin/bash

curl "http://localhost:8000/test_manys/" \
  --include \
  --request POST \
  --header "Content-Type: application/json" \
  --header "Authorization: Token ${TOKEN}" \
  --data '{
    "test_many": {
      "name": "'"${NAME}"'",
      "created_at": "'"${CREATED_AT}"'",
      "updated_at": "'"${UPDATED_AT}"'",
    }
  }'

echo
