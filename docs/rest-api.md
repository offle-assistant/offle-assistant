# REST API

---

## Auth Routes

---

### Register a user

POST /auth/register

#### Description

Creates a new user account in the system with a hashed password.
The default role is user, but it can be overridden by passing a different role.

#### Request Body

* email (string)
    The email address of the new user.

* password (string)
    The password for the new user.

* role (string, optional)
    The user’s role (e.g., admin, user). Defaults to user if not provided.

#### Responses

* 200 OK
    * Body:
    ```
    {
      "message": "User registered",
      "user": {
        "id": "<unique_user_id>",
        "email": "user@example.com",
        "role": "user"
      }
    }

    ```
    Indicates successful registration of the new user.

* 400 Bad Request
    * Body:
    ```
    {
      "detail": "Email already registered"
    }

    ```
    Returned if the email is already in use by an existing account.

#### Example Request
    ```
    POST /register
    Content-Type: application/json

    {
      "email": "john.doe@example.com",
      "password": "SecretPassword123",
      "role": "admin"
    }

    ```

#### Example Response
    ```
    {
      "message": "User registered",
      "user": {
        "id": "1234",
        "email": "john.doe@example.com",
        "role": "admin"
      }
    }

    ```

---

### Log In a User

POST /auth/login

#### Description

Authenticates an existing user using their email and password.
If the credentials are valid, returns a JWT token for accessing protected endpoints.

#### Request Body

* email (string)
    The user’s email address.

* password (string)
    The user's password.

#### Responses

* 200 OK
    * Body:
    ```
    {
      "access_token": "<jwt_token_string>",
      "token_type": "bearer"
    }

    ```
    Indicates successful authentication. The access\_token can be used in subsequent requests.

* 401 Unauthorized
    * Body:
    ```
    {
      "detail": "Invalid email or password"
    }

    ```
    Returned if the provided credentials are incorrect.

#### Example Request
```
    POST /login
    Content-Type: application/json

    {
      "email": "john.doe@example.com",
      "password": "SecretPassword123"
    }
```

#### Example Response
```
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer"
    }

```


---

## Admin routes

---

### Delete a user

DELETE /admin/users/{user\_id}/delete

#### Description

Deletes a user from the user database. Only accessible by an admin.

#### Path Parameters

* user\_id (string)

This is the unique identifier for the user.

#### Headers / Authentication

* Authorization: Bearer token containing admin privileges.

#### Responses

* 200 OK
    * Body:
    ```
    {
      "message": "User deleted successfully"
    }

    ```
    Indicates that the user was successfully deleted.

* 404 Not Found

    * Body:
    ```
    {
      "detail": "User not found"
    }

    ```
    Indicates that the user\_id doesn't exist in the database.

#### Example Request
    ```
    DELETE /users/123456/delete
    Authorization: Bearer <admin_jwt_token>

    ```

#### Example Response
    ```
    {
      "message": "User deleted successfully"
    }

    ```

---

### Update a user's role

PUT /admin/users/{user\_id}/role

#### Description

Updates a user's role in the user database. Only accessible by an admin.

#### Path Parameters

* user\_id (string)

The unique identifier for the user.

#### Request Body

* new\_role (string)

The new role to be assigned to the user. ["user", "builder", or "admin"]

#### Headers / Authentication

* Authorization: Bearer token containing admin privileges.

#### Responses

* 200 OK
    * Body:
    ```
    {
      "message": "User role updated to <new_role>"
    }

    ```
    Indicates that the user was successfully deleted.

* 404 Not Found

    * Body:
    ```
    {
      "detail": "Invalid role"
    }

    ```
    Indicates that the role is not a recognized valid role.

* 404 Not Found

    * Body:
    ```
    {
      "detail": "User not found"
    }

    ```
    Indicates that the user\_id doesn't exist in the database.

#### Example Request
    ```
    PUT /users/123456/role
    Content-Type: application/json
    Authorization: Bearer <admin_jwt_token>

    {
      "new_role": "admin"
    }

    ```

#### Example Response
    ```
    {
      "message": "User role updated to admin"
    }

    ```

---

