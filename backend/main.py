import os
import json
from typing import Optional, List, Any, Dict
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
import uvicorn
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

app = FastAPI(title="Darukaa.Earth API")

# CORS Configuration - Allow Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://darukka-earth-bj6a.vercel.app",
        "https://darukaa-earth.vercel.app",
        "https://darukka-earth.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Fallback to in-memory storage if Supabase not configured
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_KEY)

if USE_SUPABASE:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✓ Supabase client initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize Supabase: {e}")
        USE_SUPABASE = False

# Pydantic models for Authentication
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Pydantic models for Sites
class SiteCreate(BaseModel):
    name: str
    description: Optional[str] = None
    project_id: int
    geometry: Dict[str, Any]  # GeoJSON geometry
    area_hectares: Optional[float] = None
    location_info: Optional[str] = None

class SiteUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    geometry: Optional[Dict[str, Any]] = None
    area_hectares: Optional[float] = None
    location_info: Optional[str] = None

class SiteResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    project_id: int
    geometry: str  # JSON string of GeoJSON geometry
    area_hectares: Optional[float] = None
    location_info: Optional[str] = None
    created_at: Optional[str] = None

# Pydantic models for Projects
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[str] = "active"

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    status: str
    created_at: Optional[str] = None

# Temporary in-memory storage (fallback when Supabase not configured)
users_db = {}
sites_db = {}
projects_db = {}
user_id_counter = 1
site_id_counter = 1
project_id_counter = 1

# ==================== HEALTH & ROOT ====================

@app.get("/")
def read_root():
    return {
        "message": "Darukaa.Earth API is running",
        "status": "healthy",
        "storage": "Supabase" if USE_SUPABASE else "In-Memory"
    }

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "storage": "Supabase" if USE_SUPABASE else "In-Memory"
    }

# ==================== AUTHENTICATION ====================

@app.post("/api/register")
def register(user: UserRegister):
    global user_id_counter
    
    if USE_SUPABASE:
        # TODO: Implement Supabase auth
        # For now, use in-memory as fallback
        pass
    
    # In-memory storage
    if user.email in users_db:
        existing_user = users_db[user.email]
        existing_user["password"] = user.password
        existing_user["name"] = user.name or user.email.split("@")[0]
        
        return {
            "access_token": f"mock_token_{existing_user['id']}",
            "token_type": "bearer",
            "user": {
                "id": existing_user["id"],
                "email": existing_user["email"],
                "name": existing_user["name"],
                "is_admin": existing_user.get("is_admin", False)
            },
            "message": "User updated and logged in successfully"
        }
    
    users_db[user.email] = {
        "id": user_id_counter,
        "email": user.email,
        "password": user.password,
        "name": user.name or user.email.split("@")[0],
        "is_admin": user_id_counter == 1  # First user is admin
    }
    
    user_data = users_db[user.email]
    response = {
        "access_token": f"mock_token_{user_id_counter}",
        "token_type": "bearer",
        "user": {
            "id": user_data["id"],
            "email": user_data["email"],
            "name": user_data["name"],
            "is_admin": user_data["is_admin"]
        },
        "message": "Registration successful"
    }
    
    user_id_counter += 1
    return response

@app.post("/api/login")
def login(user: UserLogin):
    if user.email not in users_db:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    stored_user = users_db[user.email]
    if stored_user["password"] != user.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {
        "access_token": f"mock_token_{stored_user['id']}",
        "token_type": "bearer",
        "user": {
            "id": stored_user["id"],
            "email": stored_user["email"],
            "name": stored_user["name"],
            "is_admin": stored_user.get("is_admin", False)
        }
    }

# ==================== PROJECTS ====================

@app.get("/api/projects")
def get_projects():
    """Get all projects"""
    if USE_SUPABASE:
        try:
            response = supabase.table("projects").select("*").execute()
            return response.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # In-memory fallback
    return list(projects_db.values())

@app.get("/api/projects/{project_id}")
def get_project(project_id: int):
    """Get a specific project by ID"""
    if USE_SUPABASE:
        try:
            response = supabase.table("projects").select("*").eq("id", project_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Project not found")
            return response.data[0]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # In-memory fallback
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    return projects_db[project_id]

@app.post("/api/projects")
def create_project(project: ProjectCreate):
    """Create a new project"""
    global project_id_counter
    
    if USE_SUPABASE:
        try:
            data = {
                "name": project.name,
                "description": project.description,
                "status": project.status or "active"
            }
            response = supabase.table("projects").insert(data).execute()
            return {"data": response.data[0], "message": "Project created successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # In-memory fallback
    project_data = {
        "id": project_id_counter,
        "name": project.name,
        "description": project.description,
        "status": project.status or "active",
        "created_at": "2024-01-01T00:00:00"
    }
    projects_db[project_id_counter] = project_data
    result = {"data": project_data, "message": "Project created successfully"}
    project_id_counter += 1
    return result

@app.put("/api/projects/{project_id}")
def update_project(project_id: int, project: ProjectUpdate):
    """Update an existing project"""
    if USE_SUPABASE:
        try:
            data = {k: v for k, v in project.dict(exclude_unset=True).items() if v is not None}
            response = supabase.table("projects").update(data).eq("id", project_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Project not found")
            return {"data": response.data[0], "message": "Project updated successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # In-memory fallback
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for key, value in project.dict(exclude_unset=True).items():
        if value is not None:
            projects_db[project_id][key] = value
    
    return {"data": projects_db[project_id], "message": "Project updated successfully"}

@app.delete("/api/projects/{project_id}")
def delete_project(project_id: int):
    """Delete a project"""
    if USE_SUPABASE:
        try:
            response = supabase.table("projects").delete().eq("id", project_id).execute()
            return {"message": "Project deleted successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # In-memory fallback
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    del projects_db[project_id]
    return {"message": "Project deleted successfully"}

# ==================== SITES ====================

@app.get("/api/sites")
def get_sites():
    """Get all sites"""
    if USE_SUPABASE:
        try:
            response = supabase.table("sites").select("*").execute()
            return response.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # In-memory fallback
    return list(sites_db.values())

@app.get("/api/sites/{site_id}")
def get_site(site_id: int):
    """Get a specific site by ID"""
    if USE_SUPABASE:
        try:
            response = supabase.table("sites").select("*").eq("id", site_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Site not found")
            return response.data[0]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # In-memory fallback
    if site_id not in sites_db:
        raise HTTPException(status_code=404, detail="Site not found")
    return sites_db[site_id]

@app.post("/api/sites")
def create_site(site: SiteCreate):
    """Create a new site with polygon geometry"""
    global site_id_counter
    
    # Validate geometry is a valid GeoJSON
    if not isinstance(site.geometry, dict) or "type" not in site.geometry:
        raise HTTPException(status_code=400, detail="Invalid GeoJSON geometry")
    
    if USE_SUPABASE:
        try:
            data = {
                "name": site.name,
                "description": site.description,
                "project_id": site.project_id,
                "geometry": json.dumps(site.geometry),  # Store as JSON string
                "area_hectares": site.area_hectares,
                "location_info": site.location_info
            }
            response = supabase.table("sites").insert(data).execute()
            return {"data": response.data[0], "message": "Site created successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # In-memory fallback
    site_data = {
        "id": site_id_counter,
        "name": site.name,
        "description": site.description,
        "project_id": site.project_id,
        "geometry": json.dumps(site.geometry),  # Store as JSON string
        "area_hectares": site.area_hectares,
        "location_info": site.location_info,
        "created_at": "2024-01-01T00:00:00"
    }
    sites_db[site_id_counter] = site_data
    result = {"data": site_data, "message": "Site created successfully"}
    site_id_counter += 1
    return result

@app.put("/api/sites/{site_id}")
def update_site(site_id: int, site: SiteUpdate):
    """Update an existing site"""
    if USE_SUPABASE:
        try:
            data = {}
            for key, value in site.dict(exclude_unset=True).items():
                if value is not None:
                    if key == "geometry":
                        data[key] = json.dumps(value)
                    else:
                        data[key] = value
            
            response = supabase.table("sites").update(data).eq("id", site_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Site not found")
            return {"data": response.data[0], "message": "Site updated successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # In-memory fallback
    if site_id not in sites_db:
        raise HTTPException(status_code=404, detail="Site not found")
    
    for key, value in site.dict(exclude_unset=True).items():
        if value is not None:
            if key == "geometry":
                sites_db[site_id][key] = json.dumps(value)
            else:
                sites_db[site_id][key] = value
    
    return {"data": sites_db[site_id], "message": "Site updated successfully"}

@app.delete("/api/sites/{site_id}")
def delete_site(site_id: int):
    """Delete a site"""
    if USE_SUPABASE:
        try:
            response = supabase.table("sites").delete().eq("id", site_id).execute()
            return {"message": "Site deleted successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # In-memory fallback
    if site_id not in sites_db:
        raise HTTPException(status_code=404, detail="Site not found")
    
    del sites_db[site_id]
    return {"message": "Site deleted successfully"}

# ==================== UTILITY ENDPOINTS ====================

@app.get("/api/users")
def get_users():
    """Development endpoint to see registered users"""
    return {
        "count": len(users_db),
        "users": [
            {"id": u["id"], "email": u["email"], "name": u["name"], "is_admin": u.get("is_admin", False)} 
            for u in users_db.values()
        ]
    }

@app.delete("/api/users/clear")
def clear_users():
    """Development endpoint to clear all users - REMOVE IN PRODUCTION!"""
    global users_db, user_id_counter
    users_db = {}
    user_id_counter = 1
    return {"message": "All users cleared", "count": 0}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

