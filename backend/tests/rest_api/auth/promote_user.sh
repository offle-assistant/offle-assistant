# For this one, you need to have a user_id as the first argument and the admin token as the second argument and the new role as the third argument
curl -X PUT "http://127.0.0.1:8000/admin/users/${1}/role" \
     -H "Authorization: Bearer ${2}" \
     -H "Content-Type: application/json" \
     -d "{\"new_role\": \"${3}\"}"
