#!/bin/bash

curl "http://localhost:8000/drinks/${ID}/" \
  --include \
  --request DELETE \
  --header "Authorization: Token ${TOKEN}"

echo
