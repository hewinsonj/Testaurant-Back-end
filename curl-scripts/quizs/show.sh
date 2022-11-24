#!/bin/bash

curl "http://localhost:8000/quizs/${ID}/" \
  --include \
  --request GET \
  --header "Authorization: Token ${TOKEN}"

echo
