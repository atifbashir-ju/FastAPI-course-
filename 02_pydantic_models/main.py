# 02 - Pydantic Models
# Topics: Validation, Field, Nested models, Custom validators, Enums

from enum import Enum
from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator

app = FastAPI(title="Pydantic Models")


# ─── 1. Basic Model with Field validation ────────────────────────────────────
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, example="Ali Hassan")
    email: EmailStr = Field(..., example="ali@gmail.com")
    age: int = Field(..., ge=18, le=100, description="Age 18-100 hona chahiye")
    phone: Optional[str] = Field(None, pattern=r"^\+?[0-9]{10,13}$")


# ─── 2. Enum Fields ───────────────────────────────────────────────────────────
class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    moderator = "moderator"


class UserWithRole(BaseModel):
    name: str
    role: UserRole = UserRole.user


# ─── 3. Nested Models ─────────────────────────────────────────────────────────
class Address(BaseModel):
    street: str
    city: str
    country: str = "Pakistan"


class UserFull(BaseModel):
    name: str
    email: EmailStr
    address: Address  # Nested model


# ─── 4. Custom Validator ──────────────────────────────────────────────────────
class Product(BaseModel):
    name: str
    price: float
    discount: float = 0.0

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Price zero ya negative nahi ho sakta")
        return v

    @field_validator("discount")
    @classmethod
    def discount_range(cls, v):
        if not (0 <= v <= 100):
            raise ValueError("Discount 0-100 ke beech hona chahiye")
        return v

    @model_validator(mode="after")
    def check_discount_less_than_price(self):
        if self.discount >= self.price:
            raise ValueError("Discount price se kam hona chahiye")
        return self


# ─── 5. Response Model (hide sensitive fields) ────────────────────────────────
class UserInDB(BaseModel):
    id: int
    name: str
    email: EmailStr
    hashed_password: str  # Yeh response mein nahi aayega


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    # hashed_password yahan nahi — secure!


# ─── 6. List Model ────────────────────────────────────────────────────────────
class BulkUsers(BaseModel):
    users: List[UserCreate]
    created_by: str


# ─── Routes ──────────────────────────────────────────────────────────────────
@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):
    # DB mein save karne ka simulation
    fake_db_user = UserInDB(
        id=1,
        name=user.name,
        email=user.email,
        hashed_password="$2b$hashed...",
    )
    return fake_db_user  # response_model sirf id, name, email return karega


@app.post("/users/role")
def create_user_with_role(user: UserWithRole):
    return {"user": user, "is_admin": user.role == UserRole.admin}


@app.post("/users/full")
def create_full_user(user: UserFull):
    return {"user": user, "city": user.address.city}


@app.post("/products")
def create_product(product: Product):
    final_price = product.price - (product.price * product.discount / 100)
    return {"product": product, "final_price": round(final_price, 2)}


@app.post("/users/bulk")
def create_bulk_users(data: BulkUsers):
    return {
        "message": f"{len(data.users)} users create kiye gaye",
        "created_by": data.created_by,
    }
