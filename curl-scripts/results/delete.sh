#!/bin/bash

curl "http://localhost:8000/results/${ID}/" \
  --include \
  --request DELETE \
  --header "Authorization: Token ${TOKEN}"

echo
