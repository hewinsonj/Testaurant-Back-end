#!/bin/bash

curl "http://localhost:8000/tests/${ID}/" \
  --include \
  --request DELETE \
  --header "Authorization: Token ${TOKEN}"

echo
