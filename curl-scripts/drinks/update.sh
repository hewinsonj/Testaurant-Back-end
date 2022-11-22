#!/bin/bash

curl "http://localhost:8000/drinks/${ID}/" \
  --include \
  --request PATCH \
  --header "Content-Type: application/json" \
  --header "Authorization: Token ${TOKEN}" \
  --data '{
    "drink": {
      "name": "'"${NAME}"'",
      "ingredients": "'"${INGREDIENTS}"'",
      "garnishes": "'"${GARNISHES}"'",
      "prep_instructs": "'"${PREP_INSTRUCTS}"'",
      "glassware": "'"${GLASSWARE}"'",
      "con_egg": "'"${CON_EGG}"'",
      "con_tree_nut": "'"${CON_TREE_NUT}"'",
      "con_peanut": "'"${CON_PEANUT}"'",
      "con_shellfish": "'"${CON_SHELLFISH}"'",
      "con_soy": "'"${CON_SOY}"'",
      "con_fish": "'"${CON_FISH}"'",
      "con_wheat": "'"${CON_WHEAT}"'",
      "con_sesame": "'"${CON_SESAME}"'",
      "con_gluten": "'"${CON_GLUTEN}"'",
    }
  }'

echo
