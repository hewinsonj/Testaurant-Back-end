#!/bin/bash

curl "http://localhost:8000/results/${ID}/" \
  --include \
  --request PATCH \
  --header "Content-Type: application/json" \
  --header "Authorization: Token ${TOKEN}" \
  --data '{
    "result":     "result": {
      "score": "'"${SCORE}"'",
      "correct": "'"${CORRECTT}"'",
      "wrong": "'"${WRONG}"'",
      "total": "'"${TOTAL}"'",
      "percent": "'"${PERCENT}"'",
      "time": "'"${TIME}"'",
    }
  }'

echo
