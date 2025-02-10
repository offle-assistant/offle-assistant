curl -X POST http://127.0.0.1:8000/personas \
    -H "Content-Type: application/json" \
    -d '{
        "user_id": 3,
        "persona_name": "Offie",
        "persona_config": {
            "name": "Offie",
            "model": "llama3.2",
            "description": "A helpful assistant",
            "system_prompt": "You are a helpful assistant.",
            "temperature": 0.7,
            "rag": {
              "collections": ["test_db"],
              "threshold": 0
            }
        }
    }'
  
 
