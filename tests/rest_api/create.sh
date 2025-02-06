
curl -X POST \
    http://127.0.0.1:8000/load-persona \
    -H "Content-Type: application/json" \
    -d '{
           "persona_config": {
             "name": "Offie",
             "model": "llama3.2",
             "system_prompt": "You are a helpful assistant",
             "llm_server": {
               "hostname": "localhost",
               "port": "11434"
             },
             "vector_db_server": {
               "hostname": "localhost",
               "port": "6333"
             },
             "rag": {
               "collections": ["test_db"]
             }
           }
         }'
