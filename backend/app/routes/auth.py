from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId

from app.database import get_database
from app.schemas.auth_schemas import UserSignup, UserLogin, Token, UserResponse
from app.services.auth_service import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup):
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match."
        )
    
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection unavailable."
        )

    # Check unique email
    existing_user = await db["users"].find_one({"email": user_data.email.lower()})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    new_user_doc = {
        "name": user_data.name.strip(),
        "email": user_data.email.lower().strip(),
        "password_hash": hash_password(user_data.password),
        "created_at": datetime.utcnow()
    }

    result = await db["users"].insert_one(new_user_doc)
    user_id = str(result.inserted_id)

    user_resp = UserResponse(
        id=user_id,
        name=new_user_doc["name"],
        email=new_user_doc["email"],
        created_at=new_user_doc["created_at"]
    )

    access_token = create_access_token(data={"sub": user_id})
    return Token(access_token=access_token, token_type="bearer", user=user_resp)

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection unavailable."
        )

    user = await db["users"].find_one({"email": credentials.email.lower().strip()})
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = str(user["_id"])
    user_resp = UserResponse(
        id=user_id,
        name=user["name"],
        email=user["email"],
        created_at=user.get("created_at", datetime.utcnow())
    )

    access_token = create_access_token(data={"sub": user_id})
    return Token(access_token=access_token, token_type="bearer", user=user_resp)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        name=current_user["name"],
        email=current_user["email"],
        created_at=current_user.get("created_at", datetime.utcnow())
    )
