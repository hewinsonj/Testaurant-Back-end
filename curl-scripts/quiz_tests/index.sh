#!/bin/bash

curl "http://localhost:8000/quiz_tests/" \
  --include \
  --request GET \
  --header "Authorization: Token ${TOKEN}"

echo
