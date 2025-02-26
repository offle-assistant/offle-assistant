curl -X POST "http://127.0.0.1:8000/personas/chat/{$1}" \
     -H "Authorization: Bearer ${2}" \
     -H "Content-Type: application/json" \
     -d '{"content": "Hello there!!!"}'

