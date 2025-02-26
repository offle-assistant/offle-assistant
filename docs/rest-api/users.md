---

# Personas routes

---

## Get Current User Profile

GET /users/me


### Description

Returns the currently authenticated user’s profile information, including their ID, email, username, and any associated personas.


### Headers / Authentication

* Authorization: Bearer token containing admin privileges.

### Responses

* 200 OK
    * Body:
    ```
    {
      "user_id": "123456",
      "email": "user@example.com",
      "username": "johndoe",
      "personas": [
        {
          "12345": "Marketing persona",
          "54321": "Finance persona",
        }
      ]
    }

    ```

* 401 Unauthorized
    * Body:
    ```
    {
      "detail": "Not authenticated"
    }

    ```


### Example Request
    ```
    GET /users/me
    Authorization: Bearer <valid_jwt_token>

    ```

### Example Response
    ```
    {
      "user_id": "123456",
      "email": "user@example.com",
      "username": "johndoe",
      "personas": [
        {
          "12345": "Marketing persona",
          "54321": "Finance persona",
        }
      ]
    }

    ```

---

