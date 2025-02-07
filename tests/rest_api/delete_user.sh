curl -X DELETE \
    http://127.0.0.1:8000/users/1 \
    -H "Content-Type: application/json" \
    -d '{
        "user_id": 1,
    }'


