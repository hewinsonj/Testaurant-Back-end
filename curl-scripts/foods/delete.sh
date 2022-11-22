#!/bin/bash

curl "http://localhost:8000/foods/${ID}/" \
  --include \
  --request DELETE \
  --header "Authorization: Token ${TOKEN}"

echo
