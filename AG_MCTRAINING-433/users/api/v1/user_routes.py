from fastapi import APIRouter, Depends, HTTPException

from users.core.dependencies import get_user_service
from users.models.user import UserCreateRequest, UserUpdateRequest
from users.services.user_service import UserService

router = APIRouter(tags=["users"])


@router.get("/users")
async def list_users(
    service: UserService = Depends(get_user_service),
):
    return service.list_users()


@router.post("/users", status_code=201)
async def create_user(
    body: UserCreateRequest,
    service: UserService = Depends(get_user_service),
):
    user_id = service.create_user(body.model_dump())
    return {"message": "User created", "userId": user_id}


@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
):
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    body: UserUpdateRequest,
    service: UserService = Depends(get_user_service),
):
    service.update_user(user_id, body.model_dump())
    return {"message": "Event sent"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
):
    service.delete_user(user_id)
    return {"message": "User deleted"}
