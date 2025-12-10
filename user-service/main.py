from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import List
import uvicorn

from database import users_collection, init_db
from models import UserCreate, UserResponse, UserUpdate, LoginRequest, Token, TokenData
from auth import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    get_current_user,
    require_admin
)
from config import settings

app = FastAPI(
    title="User Service",
    version="1.0.0",
    description="Authentication and User Management Service"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Initialize database on startup"""
    try:
        init_db()
        print("User service started successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")


@app.get("/")
def root():
    return {"message": "User Service is running!"}


@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate):
    """Register a new user"""
    # Check if user already exists
    existing_user = users_collection.find_one({
        "$or": [
            {"email": user.email},
            {"username": user.username}
        ]
    })
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create user document
    user_dict = user.model_dump()
    user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()
    user_dict["is_active"] = True
    
    # Insert into database
    result = users_collection.insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)
    
    return UserResponse(**user_dict)


@app.post("/login", response_model=Token)
def login(login_data: LoginRequest):
    """Login and get access token"""
    # Find user by username
    user = users_collection.find_one({"username": login_data.username})
    
    if not user or not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@app.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """Get current user information"""
    user = users_collection.find_one({"username": current_user.username})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user["_id"] = str(user["_id"])
    return UserResponse(**user)


@app.get("/users", response_model=List[UserResponse])
def list_users(
    role: str = None,
    current_user: TokenData = Depends(require_admin)
):
    """List all users (admin only)"""
    query = {}
    if role:
        query["role"] = role
    
    users = []
    for user in users_collection.find(query):
        user["_id"] = str(user["_id"])
        users.append(UserResponse(**user))
    
    return users


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get user by ID.
    Admins and trainers can view any user. Members can only view themselves.
    """
    from bson import ObjectId
    
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Authorization: admin & trainer can see any; member only self
    if current_user.role not in ("admin", "trainer") and user.get("username") != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    user_id_str = str(user["_id"])
    user["_id"] = user_id_str
    # also provide id field for clients that prefer it
    user["id"] = user_id_str
    return UserResponse(**user)


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    """Update user information"""
    from bson import ObjectId
    
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Users can update their own profile or admins can update anyone
    if current_user.role != "admin" and user["username"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Prepare update data
    update_data = user_update.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
    
    # Get updated user
    updated_user = users_collection.find_one({"_id": ObjectId(user_id)})
    updated_user["_id"] = str(updated_user["_id"])
    
    return UserResponse(**updated_user)


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    current_user: TokenData = Depends(require_admin)
):
    """Delete user (admin only)"""
    from bson import ObjectId
    
    try:
        result = users_collection.delete_one({"_id": ObjectId(user_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return None


@app.post("/verify-token")
def verify_token(current_user: TokenData = Depends(get_current_user)):
    """Verify if a token is valid"""
    return {
        "valid": True,
        "username": current_user.username,
        "role": current_user.role
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
