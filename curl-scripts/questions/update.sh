#!/bin/bash

curl "http://localhost:8000/questions/${ID}/" \
  --include \
  --request PATCH \
  --header "Content-Type: application/json" \
  --header "Authorization: Token ${TOKEN}" \
  --data '{
    "question": {
      "question_str": "'"${QUESTION_STR}"'",
      "option1": "'"${OPTION1}"'",
      "option2": "'"${OPTION2}"'",
      "option3": "'"${OPTION3}"'",
      "option4": "'"${OPTION4}"'",
      "answer": "'"${ANSWER}"'"
    }
  }'

echo
