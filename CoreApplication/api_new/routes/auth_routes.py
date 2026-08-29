from fastapi import APIRouter,Depends,HTTPException,status
from pydantic import BaseModel, EmailStr
from bson import ObjectId#ObjectId handles user id from database
from datetime import timedelta
#INTERNAL IMPORT
from ..database.db_config import db
from ..utils.auth_utils import (#auth_utils:password hashing+JWT generation/verification
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token
)
from ..models.user_model import User
#INITIALISE ROUTER
router=APIRouter(#APIR outer helps you organize you authentication routes separately from other modules 
    prefix="/auth",#Every endpoint here will start with /auth
    tags=["Authentication"]
)

#REGISTER ENDPOINT
@router.post("/register")
async def register_user(user:User):
    #CHECK IF USER ALREADY EXISTS
    existing_user=await db["users"].find_one({"email":user.email})
    if existing_user:
        raise HTTPException(status_code=400,detail="User already registered")
     # Hash the password
    hashed_password = get_password_hash(user.password)
    # Create user document
    new_user = {
        "name": user.name,
        "email": user.email,
        "password": hashed_password,
        "role": user.role
    }
    #Insert into MongoDB
    result = await db["users"].insert_one(new_user)
    #Response
    return {
        "message": "User registered successfully",
        "user_id": str(result.inserted_id)
    }
#LOGIN
@router.post("/login")
async def login_user(login_data: dict):
    email = login_data.get("email")
    password = login_data.get("password")
    # Find user in DB
    user = await db["users"].find_one({"email": email})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    # Verify password
    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    # Create JWT token
    access_token = create_access_token({"email": user["email"], "role": user["role"]})
    # Return token + basic info
    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"],
        "name": user["name"]
    }
#Logout endpoint
@router.post("/logout")
async def logout_user():
    return {"message": "Logout successful"}
#Verify Token Route
@router.get("/verify-token")
async def verify_token(token: str):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {
        "status": "success",
        "message": "Token is valid",
        "user": payload["email"],
        "role": payload["role"]
    }