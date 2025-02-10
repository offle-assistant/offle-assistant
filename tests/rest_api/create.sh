curl -X POST \
    http://127.0.0.1:8000/load-persona \
    -H "Content-Type: application/json" \
    -d '{
           "persona_config": {
             "name": "Offie",
             "model": "llama3.2",
             "description": "A helpfule assistant",
             "system_prompt": "You are a helpful assistant.",
             "temperature": .7
             "rag": {
               "collections": ["test_db"],
               "threshold": .6
             }
           }
         }'
