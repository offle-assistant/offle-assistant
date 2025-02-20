# For this one, you need to have a persona_id as the first argument and the user token as the second argument
curl -X PUT "http://127.0.0.1:8000/personas/build/${1}" \
     -H "Authorization: Bearer ${2}" \
     -H "Content-Type: application/json" \
     -d '{"name": "Updated AI Helper"}'
