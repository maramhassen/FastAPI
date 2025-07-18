from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    email: EmailStr


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_default: bool
    can_delete: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class UpdateEmail(BaseModel):
    email: EmailStr
    


class ProduitMini(BaseModel):
    id: int
    name: str
    price: float
    description: str
    available: bool
    

    model_config = {"from_attributes": True}

class UserWithProduitsResponse(UserResponse):
    produits: List[ProduitMini] = []  

    model_config = {"from_attributes": True}

class StandardResponse(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

# Product 
class ProduitBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    available: bool = True

class ProduitCreate(ProduitBase):
    user_id: int

class UserInfo(BaseModel):
    id: int
    name: str  
    email: EmailStr

    class Config:
        orm_mode = True

class ProduitResponse(ProduitBase):
    id: int
    user_id: int
    user: UserInfo

    class Config:
        orm_mode = True

