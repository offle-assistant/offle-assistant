---

# Personas routes

---

## Get all personas created by the current user

GET /personas/owned

### Description

Retrieves all personas associated with the currently authenticated user as creator.


### Headers / Authentication

* Authorization: Bearer token containing admin privileges.

### Responses

* 200 OK
    * Body:
    ```
    {
      "PERSONA_ID_1": "PERSONA_NAME_1",
      "PERSONA_ID_2": "PERSONA_NAME_2",
    }
    ```
    Indicates that the user was successfully deleted.


### Example Request
    ```
    GET /personas
    Authorization: Bearer <user_jwt_token>

    ```

### Example Response
    ```
    {
      "12381230": "Offie",
      "10297411": "Jeff",
    }

    ```

---

## Create a Persona

POST /personas/build

### Description

Allows a user with the builder (or admin) role to create a new persona.
Requires providing the creator\_id (and other fields) in the request body.

### Headers / Authentication

* Authorization: Bearer token containing admin privileges.

### Request Body

The request body is a JSON object representing a PersonaModel.
For example, it might include:

* persona\_name (string) – The name of the persona.
* creator\_id (string) – The ID of the user who will own this persona.
* description (string, optional) – A short description of the persona.
* system\prompt (string, optional)
* model (string, optional)
* temperature (float, optional)
* rag (dict)
    * db\_collections (list[string]) - list of collections this persona has access to.
    * query\_threshold (float) - Similarity threshold for document retrieval
    * query\_metric (string) - "cosine" or "euclidean", the metric for determining similarity.


### Responses

* 200 OK
    * Body:
    ```
    {
      "message": "Persona created successfully",
      "persona_id": "12345",
      "persona_name": "My New Persona"
    }

    ```
    Indicates that the persona was successfully created.

* 404 Not Found
    * Body:
    ```
    {
      "detail": "Invalid user_id: User does not exist"
    }

    ```
    Returned if the creator\_id does not match an existing user in the database.

### Example Request
    ```
    POST /personas/build
    Content-Type: application/json
    Authorization: Bearer <builder_or_admin_jwt_token>

    {
      "persona_name": "Marketing Persona",
      "creator_id": "user123",
      "description": "Persona to target marketing campaigns."
    }


    ```

### Example Response
    ```
    {
      "message": "Persona created successfully",
      "persona_id": "67890",
      "persona_name": "Marketing Persona"
    }

    ```

---

## Update a Persona

PUT /personas/build/{persona\_id}

### Description

Allows a user with the builder (or admin) role to update an existing persona by its ID.

### Path Parameters

* persona\_id (string)
    The unique identifier of the persona to be updated.

### Headers / Authentication

* Authorization: Bearer token for the logged-in user.

### Request Body

A JSON object representing the updates to apply.
For example, if you have a PersonaUpdate model, it might include:

* persona\_name (string) – The name of the persona.
* creator\_id (string) – The ID of the user who will own this persona.
* description (string, optional) – A short description of the persona.
* system\prompt (string, optional)
* model (string, optional)
* temperature (float, optional)
* rag (dict)
    * db\_collections (list[string]) - list of collections this persona has access to.
    * query\_threshold (float) - Similarity threshold for document retrieval
    * query\_metric (string) - "cosine" or "euclidean", the metric for determining similarity.


### Responses

* 200 OK
    * Body:
    ```
    {
      "message": "Persona updated successfully"
    }


    ```
    Indicates that the persona was successfully updated.

* 404 Not Found
    * Body:
    ```
    {
      "detail": "Persona not found"
    }

    ```
    Returned if the persona\_id does not match an existing persona in the database.

### Example Request
    ```
    PUT /personas/67890
    Content-Type: application/json
    Authorization: Bearer <builder_or_admin_jwt_token>

    {
      "persona_name": "Marketing Persona v2",
      "description": "Refined marketing persona."
    }



    ```

### Example Response
    ```
    {
      "message": "Persona updated successfully"
    }

    ```

---

## Get Persona Message History for a user

GET /personas/{persona\_id}/message\_history

### Description

Retrieves the message history associated with a specific persona for the currently authenticated user.

### Path Parameters

* persona\_id (string)
    The unique identifier of the persona to be updated.

### Headers / Authentication

* Authorization: Bearer token for the logged-in user. 

### Responses

* 200 OK
    * Body:
    ```
    {
      "message": "Persona updated successfully"
    }


    ```
    Indicates that the persona was successfully updated.

* 404 Not Found
    * Body:
    ```
    {
      "persona\_id": "abc123",
      "messages": [
        {
          "id": "12345",
          "title": "Marketing questions",
          "description": "a conversation about marketing",
          "messages": [],
          "created\_at": "2025-02-24T10:45:00Z"
        },
        {
          "id": "54321",
          "title": "Finance technology",
          "description": "A conversation about finance technology",
          "messages": [],
          "created\_at": "2025-02-24T10:45:00Z"
        }
      ]
    }

    ```
    Returned if the persona\_id does not match an existing persona in the database.

### Example Request
    ```
    GET /personas/abc123/message_history
    Authorization: Bearer <user_jwt_token>

    ```

### Example Response
    ```
    {
      "persona\_id": "abc123",
      "messages": [
        {
          "id": "12345",
          "title": "Marketing questions",
          "description": "a conversation about marketing",
          "messages": [],
          "created\_at": "2025-02-24T10:45:00Z"
        },
        {
          "id": "54321",
          "title": "Finance technology",
          "description": "A conversation about finance technology",
          "messages": [],
          "created\_at": "2025-02-24T10:45:00Z"
        }
      ]
    }

    ```
---

## Send a message to a Persona

POST /personas/{persona\_id}/chat

### Description

Allows a user to send a message to a persona and receive a response.
The endpoint also saves the message history for future retrieval.

### Request Body

```
    {
      "message_history_id": "12345",
      "content": "How can you help me with marketing strategies?"
    }

```

### Path Parameters

* persona\_id (string)
    The unique identifier of the persona to be updated.

### Headers / Authentication

* Authorization: Bearer token for the logged-in user. 

### Responses

* 200 OK
    * Body:
    ```
    {
      "persona_id": "54321",
      "message_history_id": "12345",
      "response": "I can help you by analyzing target demographics, refining brand messaging, and suggesting campaign strategies.",
      "rag_hit": {
        "file_name": "important document",
        "doc_path": "path/to/document.md",
        "document_string": "This is very important information right here.",
        "euclidean_distance": "0.4",
        "cosine_similarity": "0.6",
        "success": "true"
      }
    }

    ```

* 404 Not Found
    * Body:
    ```
    {
      "detail": "Message content is required"
    }

    ```
    Returned if the request body does not include the message field or if it’s empty.

### Example Request
    ```
    POST /personas/abc123/chat
    Content-Type: application/json
    Authorization: Bearer <user_jwt_token>

    {
      "message_history_id": "12345",
      "content": "How can you help me with marketing strategies?"
    }

    ```

### Example Response
    ```
    {
      "persona_id": "54321",
      "message_history_id": "12345",
      "response": "I can help you by analyzing target demographics, refining brand messaging, and suggesting campaign strategies.",
      "rag_hit": {
        "file_name": "important document",
        "doc_path": "path/to/document.md",
        "document_string": "This is very important information right here.",
        "euclidean_distance": "0.4",
        "cosine_similarity": "0.6",
        "success": "true"
      }
    }

    ```
---
