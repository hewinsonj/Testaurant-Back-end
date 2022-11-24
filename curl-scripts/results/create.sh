#!/bin/bash

curl "http://localhost:8000/results/" \
  --include \
  --request POST \
  --header "Content-Type: application/json" \
  --header "Authorization: Token ${TOKEN}" \
  --data '{
    "result": {
      "score": "'"${SCORE}"'",
      "correct": "'"${CORRECT}"'",
      "wrong": "'"${WRONG}"'",
      "total": "'"${TOTAL}"'",
      "percent": "'"${PERCENT}"'",
      "time": "'"${TIME}"'",
      "created_at": "'"${CREATED_AT}"'",
      "updated_at": "'"${UPDATED_AT}"'",
    }
  }'

echo
