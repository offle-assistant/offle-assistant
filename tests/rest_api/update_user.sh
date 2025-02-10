curl -X PUT \
    http://127.0.0.1:8000/users/1 \
    -H "Content-Type: application/json" \
    -d '{
        "user_id": 1,
        "first_name": "Jeff",
        "last_name": "Tatum",
        "email": "super@sick.yes"
    }'


