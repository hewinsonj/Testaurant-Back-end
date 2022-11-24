#!/bin/bash

curl "http://localhost:8000/quizs/" \
  --include \
  --request POST \
  --header "Content-Type: application/json" \
  --header "Authorization: Token ${TOKEN}" \
  --data '{
    "quiz": {
      "name": "'"${NAME}"'",
      "created_at": "'"${CREATED_AT}"'",
      "updated_at": "'"${UPDATED_AT}"'",
    }
  }'

echo
