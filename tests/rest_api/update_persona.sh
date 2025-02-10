curl -X PATCH http://127.0.0.1:8000/personas/2 \
    -H "Content-Type: application/json" \
    -d '{
        "persona_name": "Jeff",
        "persona_id": 2,
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
  
 

