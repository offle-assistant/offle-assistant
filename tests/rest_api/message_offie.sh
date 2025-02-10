curl -X POST http://127.0.0.1:8000/chat \
    -H "Content-Type: application/json" \
    -d '{
        "user_id": "Reed",
        "persona_config": {
            "persona_id": "4321",
            "name": "Offie",
            "model": "llama3.2",
            "description": "A helpful assistant",
            "system_prompt": "You are a helpful assistant.",
            "temperature": 0.7,
            "rag": {
              "collections": ["test_db"],
              "threshold": 0.9
            }
        },
        "content": "Do you remember my name?"
    }'
  
 
