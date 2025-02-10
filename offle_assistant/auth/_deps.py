from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from bson import ObjectId

from ._utils import SECRET_KEY, ALGORITHM
from offle_assistant.database import users_collection

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Extracts user from JWT token & verifies authentication."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid authentication credentials"
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if not user_id:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise credentials_exception

    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise credentials_exception

    return user


async def admin_required(user: dict = Depends(get_current_user)):
    """Ensures only admins can access a route."""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


async def builder_required(user: dict = Depends(get_current_user)):
    """Ensures only builders or admins can access a route."""
    if user.get("role") not in ["builder", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Builder or admin access required"
        )
    return user
