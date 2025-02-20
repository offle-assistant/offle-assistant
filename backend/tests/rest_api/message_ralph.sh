curl -X POST http://127.0.0.1:8000/chat \
    -H "Content-Type: application/json" \
    -d '{
        "user_id": "Reed",
        "persona_config": {
            "persona_id": "1234",
            "name": "Ralph",
            "model": "llama3.2",
            "system_prompt": "You are a grumpy sys admin.",
            "description": "A helpfule assistant",
            "temperature": 0.7,
            "rag": {
              "collections": ["test_db"],
              "threshold": 0.6
            }
        },
        "content": "Do you remember my name?"
    }'
 
