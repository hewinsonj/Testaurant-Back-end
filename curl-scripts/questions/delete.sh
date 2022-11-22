#!/bin/bash

curl "http://localhost:8000/questions/${ID}/" \
  --include \
  --request DELETE \
  --header "Authorization: Token ${TOKEN}"

echo
