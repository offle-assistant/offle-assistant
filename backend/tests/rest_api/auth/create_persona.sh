# To use this, you need a token. Run "login.sh" and then copy the token and paste it as an argument to this script like " sh ./create_persona.sh jwt.token.here "
curl -X POST "http://127.0.0.1:8000/personas/build" \
     -H "Authorization: Bearer ${1}" \
     -H "Content-Type: application/json" \
     -d '{"name": "AI Helper", "description": "Your AI assistant"}'
