#!/bin/bash

curl "http://localhost:8000/foods/" \
  --include \
  --request GET \
  --header "Authorization: Token ${TOKEN}"

echo
