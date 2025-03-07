---

# Admin routes

---

## Delete a user

DELETE /admin/users/{user\_id}/delete

### Description

Deletes a user from the user database. Only accessible by an admin.

### Path Parameters

* user\_id (string)

This is the unique identifier for the user.

### Headers / Authentication

* Authorization: Bearer token containing admin privileges.

### Responses

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

* 403 Not Found

    * Body:
    ```
    {
      "detail": "Admin access required"
    }

    ```
    Indicates that the user needs admin access to perform the delete.

### Example Request
    ```
    DELETE /users/123456/delete
    Authorization: Bearer <admin_jwt_token>

    ```

### Example Response
    ```
    {
      "message": "User deleted successfully"
    }

    ```

---

## Update a user's role

PUT /admin/users/{user\_id}/role

### Description

Updates a user's role in the user database. Only accessible by an admin.

### Path Parameters

* user\_id (string)

The unique identifier for the user.

### Request Body

* new\_role (string)

The new role to be assigned to the user. ["user", "builder", or "admin"]

### Headers / Authentication

* Authorization: Bearer token containing admin privileges.

### Responses

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

### Example Request
    ```
    PUT /users/123456/role
    Content-Type: application/json
    Authorization: Bearer <admin_jwt_token>

    {
      "new_role": "admin"
    }

    ```

### Example Response
    ```
    {
      "message": "User role updated to admin"
    }

    ```

---
