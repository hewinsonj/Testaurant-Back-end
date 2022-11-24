#!/bin/bash

curl "http://localhost:8000/test_thiss/${ID}/" \
  --include \
  --request DELETE \
  --header "Authorization: Token ${TOKEN}"

echo
