#!/bin/bash

curl "http://localhost:8000/quizs/${ID}/" \
  --include \
  --request DELETE \
  --header "Authorization: Token ${TOKEN}"

echo
