# To use this, you need a user_id as the first argument and a token as the second.
curl -X DELETE "http://127.0.0.1:8000/admin/users/${1}/delete" \
     -H "Authorization: Bearer ${2}" \
     -H "Content-Type: application/json"

