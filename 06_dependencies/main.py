# 06 - Dependency Injection
# Topics: Depends(), reusable logic, class-based deps, chained deps

from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Header, Query

app = FastAPI(title="Dependency Injection")


# ─── 1. Simple Function Dependency ───────────────────────────────────────────
def get_pagination(skip: int = Query(0, ge=0), limit: int = Query(10, le=100)):
    return {"skip": skip, "limit": limit}


@app.get("/items")
def get_items(pagination: dict = Depends(get_pagination)):
    # Har route mein ek hi pagination logic
    return {"skip": pagination["skip"], "limit": pagination["limit"]}


@app.get("/products")
def get_products(pagination: dict = Depends(get_pagination)):
    return {"products": [], "pagination": pagination}


# ─── 2. Authentication Dependency ────────────────────────────────────────────
def verify_api_key(x_api_key: str = Header(...)):
    valid_keys = ["secret-key-123", "admin-key-456"]
    if x_api_key not in valid_keys:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key


@app.get("/secure-data")
def get_secure_data(api_key: str = Depends(verify_api_key)):
    return {"message": "Yeh secure data hai", "api_key_used": api_key}


# ─── 3. Class-Based Dependency ───────────────────────────────────────────────
class FilterParams:
    def __init__(
        self,
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock: bool = True,
    ):
        self.search = search
        self.min_price = min_price
        self.max_price = max_price
        self.in_stock = in_stock


@app.get("/shop/products")
def filter_products(filters: FilterParams = Depends()):
    return {
        "search": filters.search,
        "price_range": f"{filters.min_price} - {filters.max_price}",
        "in_stock": filters.in_stock,
    }


# ─── 4. Chained Dependencies ─────────────────────────────────────────────────
# Dep 1: verify token
def get_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token format galat hai")
    return authorization.split(" ")[1]


# Dep 2: get user from token (get_token pe depend karta hai)
def get_current_user(token: str = Depends(get_token)):
    fake_users = {"valid-token-abc": {"id": 1, "name": "Ali", "role": "admin"}}
    user = fake_users.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="Token invalid hai")
    return user


# Dep 3: admin check (get_current_user pe depend karta hai)
def require_admin(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Sirf admin access kar sakta hai")
    return user


@app.get("/admin/dashboard")
def admin_dashboard(admin: dict = Depends(require_admin)):
    return {"message": f"Admin panel — Welcome {admin['name']}"}


@app.get("/profile")
def my_profile(user: dict = Depends(get_current_user)):
    return {"user": user}


# ─── 5. Dependency with yield (DB session pattern) ───────────────────────────
def get_fake_db():
    db = {"connected": True, "name": "fake_db"}
    print("DB connection khola")
    try:
        yield db
    finally:
        print("DB connection band kiya")  # Cleanup


@app.get("/db-test")
def test_db(db: dict = Depends(get_fake_db)):
    return {"db_status": db["connected"], "db_name": db["name"]}
