#!/bin/bash

curl "http://localhost:8000/results/" \
  --include \
  --request POST \
  --header "Content-Type: application/json" \
  --header "Authorization: Token ${TOKEN}" \
  --data '{
    "result": {
      "score": "'"${SCORE}"'",
      "correct": "'"${CORRECTT}"'",
      "wrong": "'"${WRONG}"'",
      "total": "'"${TOTAL}"'",
      "percent": "'"${PERCENT}"'",
      "time": "'"${TIME}"'",
    }
  }'

echo
