from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.schemas import UpdateEmail
from app.database import get_db
from app.model.user import User
from app.schemas import UserCreate, UserResponse, StandardResponse, UserWithProduitsResponse
from app.redis_client import redis_manager
from fastapi import Path
from fastapi import Body
import logging
from app.service.elasticsearch_service import index_user, search_users as es_search_users
from sqlalchemy.orm import joinedload

from fastapi import FastAPI, Query
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/users/", response_model=StandardResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        return StandardResponse(code=400, message="Email already exists", data=None)
    db_user = User(
        name=user.name,
        email=user.email,
        is_default=False,
        can_delete=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Indexer dans Elasticsearch
    await index_user(db_user)
  
    users = db.query(User).filter(User.deleted_at == None).all()
    user_data = [UserResponse.model_validate(u).model_dump(mode='json') for u in users]
    await redis_manager.set_json("all_users", user_data)
    result = UserResponse.model_validate(db_user).model_dump(mode='json')
    return StandardResponse(code=200, message="successful", data=result)



@router.get("/users/deleted", response_model=StandardResponse)
def get_soft_deleted_users(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.deleted_at.is_not(None)).all()
    user_data = [UserResponse.model_validate(u).model_dump(mode='json') for u in users]
    return StandardResponse(code=200, message="successful", data=user_data)

@router.get("/users/", response_model=StandardResponse)
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User)\
              .options(joinedload(User.produits))\
              .filter(User.deleted_at == None)\
              .all()

    # Convertir avec model_validate seulement
    data = [UserWithProduitsResponse.model_validate(u) for u in users]

    return StandardResponse(code=200, message="successful", data=data)


@router.get("/{user_id}", response_model=UserWithProduitsResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

@router.put("/users/{user_id}", response_model=StandardResponse)
async def update_email_by_id(
    user_id: int,
    payload: UpdateEmail = Body(..., description="New email to update"),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.email = payload.email
    db.commit()
    db.refresh(user)

    await redis_manager.delete("all_users")

    result = UserResponse.model_validate(user).model_dump(mode='json')
    return StandardResponse(code=200, message="Email updated successfully", data=result)


@router.delete("/users/{user_id}/soft", response_model=StandardResponse)
async def soft_delete(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return StandardResponse(code=404, message="User not found", data=None)
    if not user.can_delete:
        return StandardResponse(code=403, message="This user cannot be deleted", data=None)
    user.deleted_at = datetime.utcnow()
    db.commit()
    await redis_manager.delete("all_users")
    user_data = UserResponse.model_validate(user).model_dump(mode='json')
    return StandardResponse(code=200, message="User soft-deleted successfully", data=user_data)


@router.delete("/users/{user_id}/hard", response_model=StandardResponse)
async def hard_delete(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return StandardResponse(code=404, message="User not found", data=None)
        if not user.can_delete:
            return StandardResponse(code=403, message="This user cannot be deleted", data=None)
        if user.deleted_at is None:
            return StandardResponse(code=400, message="User must be soft deleted before hard delete.", data=None)
        user_data = UserResponse.model_validate(user).model_dump(mode='json')
        db.delete(user)
        db.commit()
        await redis_manager.delete("all_users")
        return StandardResponse(code=200, message="User hard-deleted successfully", data=user_data)
    except Exception as e:
        return StandardResponse(code=500, message=f"Internal Server Error: {str(e)}", data=None)

@router.put("/users/{user_id}/restore", response_model=StandardResponse)
async def restore(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.deleted_at:
        return StandardResponse(code=404, message="User not found or not soft-deleted", data=None)
    user.deleted_at = None
    db.commit()
    await redis_manager.delete("all_users")
    return StandardResponse(code=200, message="successful", data=None)


async def get_or_set_cache(key: str, db_fetch_func):
    cached = await redis_manager.get_json(key)
    if cached:
        logger.info(f"✅ Data retrieved from Redis cache with key: {key}")
        return cached, True
    logger.info(f"📦 Cache miss for key: {key}, querying DB...")
    data = db_fetch_func()
    await redis_manager.set_json(key, data)
    logger.info(f"✅ Data cached in Redis with key: {key}")
    return data, False


@router.get("/users/search/", response_model=StandardResponse)
async def search_users(query: str = Query(..., description="Search query for users", max_length=256)):
    try:
        results = await es_search_users(query)
        # Extraire les données utiles, typiquement _source contient le document user
        users = [hit["_source"] for hit in results]
        return StandardResponse(code=200, message="successful", data=users)
    except Exception as e:
        return StandardResponse(code=500, message=f"Elasticsearch error: {str(e)}", data=None)