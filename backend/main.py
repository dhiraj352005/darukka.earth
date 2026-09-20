from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import uvicorn

app = FastAPI(title="Darukaa.Earth API")

# CORS Configuration - Allow Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://darukka-earth-bj6a.vercel.app",  # Your actual Vercel URL
        "https://darukaa-earth.vercel.app",       # Alternative spelling
        "https://darukka-earth.vercel.app",       # Alternative spelling
        "http://localhost:5173",                   # Local development (Vite)
        "http://localhost:3000",                   # Alternative local port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    message: str

# Temporary in-memory storage (replace with database in production)
users_db = {}
user_id_counter = 1

@app.get("/")
def read_root():
    return {"message": "Darukaa.Earth API is running", "status": "healthy"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/register", response_model=UserResponse)
def register(user: UserRegister):
    global user_id_counter
    
    # Check if user already exists
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Store user (in production, hash the password!)
    users_db[user.email] = {
        "id": user_id_counter,
        "email": user.email,
        "password": user.password,  # TODO: Hash this in production!
        "name": user.name or user.email.split("@")[0]
    }
    
    response = UserResponse(
        id=user_id_counter,
        email=user.email,
        name=users_db[user.email]["name"],
        message="Registration successful"
    )
    
    user_id_counter += 1
    return response

@app.post("/api/login", response_model=UserResponse)
def login(user: UserLogin):
    # Check if user exists
    if user.email not in users_db:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check password (in production, compare hashed passwords!)
    stored_user = users_db[user.email]
    if stored_user["password"] != user.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return UserResponse(
        id=stored_user["id"],
        email=stored_user["email"],
        name=stored_user["name"],
        message="Login successful"
    )

@app.get("/api/users")
def get_users():
    """Development endpoint to see registered users"""
    return {
        "count": len(users_db),
        "users": [
            {"id": u["id"], "email": u["email"], "name": u["name"]} 
            for u in users_db.values()
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
