#!/bin/bash

curl "http://localhost:8000/quizs/" \
  --include \
  --request GET \
  --header "Authorization: Token ${TOKEN}"

echo
