# $ sh get_persona_dict.sh jwt.token.here
curl -X GET "http://127.0.0.1:8000/personas/owned" \
     -H "Authorization: Bearer ${1}"

