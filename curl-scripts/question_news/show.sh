#!/bin/bash

curl "http://localhost:8000/question_news/${ID}/" \
  --include \
  --request GET \
  --header "Authorization: Token ${TOKEN}"

echo
