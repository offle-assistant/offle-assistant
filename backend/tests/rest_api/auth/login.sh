curl -X POST "http://127.0.0.1:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@admin.com", "password": "admin"}'

# This is what the return will look like
# {"access_token": "your.jwt.token", "token_type": "bearer"}
