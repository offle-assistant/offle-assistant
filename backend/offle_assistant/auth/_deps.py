from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from bson import ObjectId

from ._utils import SECRET_KEY, ALGORITHM
from offle_assistant.database import get_user_by_id
from offle_assistant.models import UserModel
from offle_assistant.dependencies import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db=Depends(get_db)
) -> UserModel:
    """Extracts user from JWT token & verifies authentication."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid authentication credentials"
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = str(payload.get("user_id"))
        if not user_id:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise credentials_exception

    user_dict = await get_user_by_id(user_id, db=db)
    if not user_dict:
        raise credentials_exception

    user_dict["_id"] = str(user_dict["_id"])
    user_model = UserModel(**user_dict)

    return user_model


async def admin_required(
    user: UserModel = Depends(get_current_user)
) -> UserModel:
    """Ensures only admins can access a route."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


async def builder_required(
    user: UserModel = Depends(get_current_user)
) -> UserModel:
    """Ensures only builders or admins can access a route."""
    if user.role not in ["builder", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Builder or admin access required"
        )
    return user
