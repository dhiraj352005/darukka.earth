import os
import json
import math
from datetime import datetime, timedelta
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

class AnalyticsResponse(BaseModel):
    site_id: int
    area_hectares: float
    estimated_trees: int
    estimated_biomass_tons: float
    co2_sequestration_annual: float
    co2_offset_vehicles: int
    canopy_cover_percentage: float
    soil_health_index: float
    biodiversity_score: int
    water_retention_capacity: float
    historical_data: Dict[str, Any]

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

# ==================== HELPER FUNCTIONS ====================

def calculate_polygon_area_hectares(geometry: Dict[str, Any]) -> float:
    """
    Calculate the approximate area of a polygon in hectares.
    Uses simple spherical geometry approximation.
    """
    try:
        if geometry["type"] != "Polygon":
            return 0.0
        
        coordinates = geometry["coordinates"][0]  # Get outer ring
        if len(coordinates) < 3:
            return 0.0
        
        # Convert to radians and calculate area using shoelace formula
        area_sq_meters = 0.0
        n = len(coordinates) - 1  # Exclude closing coordinate
        
        for i in range(n):
            lon1, lat1 = coordinates[i]
            lon2, lat2 = coordinates[(i + 1) % n]
            
            # Convert to radians
            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            lon1_rad = math.radians(lon1)
            lon2_rad = math.radians(lon2)
            
            # Earth radius in meters
            R = 6371000
            
            # Calculate area contribution
            area_sq_meters += (lon2_rad - lon1_rad) * (2 + math.sin(lat1_rad) + math.sin(lat2_rad)) * R * R / 2
        
        area_sq_meters = abs(area_sq_meters)
        
        # Convert square meters to hectares (1 hectare = 10,000 sq meters)
        return round(area_sq_meters / 10000, 2)
    
    except Exception as e:
        print(f"Error calculating area: {e}")
        return 0.0

def calculate_environmental_analytics(site_id: int, area_hectares: float, created_at: str = None) -> Dict[str, Any]:
    """
    Calculate environmental analytics based on site area and time since creation.
    Uses research-based estimates and industry standards.
    """
    
    # If no creation date provided, use current date
    if not created_at:
        created_at = datetime.now().isoformat()
    
    try:
        site_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    except:
        site_date = datetime.now()
    
    months_active = max(1, (datetime.now() - site_date).days / 30)
    years_active = months_active / 12
    
    # Base calculations (conservative estimates)
    # Source: FAO, IPCC guidelines
    
    # Trees per hectare: 400-1000 for reforestation (using 600 as average)
    trees_per_hectare = 600
    estimated_trees = int(area_hectares * trees_per_hectare * min(years_active, 1))  # Cap at 1 year
    
    # Biomass: Average tree stores ~250kg after 1 year, increasing over time
    biomass_per_tree = 250 * min(years_active, 5) / 5  # Max at 5 years
    estimated_biomass_tons = round((estimated_trees * biomass_per_tree) / 1000, 2)
    
    # CO2 Sequestration: ~10-15 tons CO2/hectare/year for young forests
    co2_per_hectare_annual = 12.5
    co2_sequestration_annual = round(area_hectares * co2_per_hectare_annual * min(years_active, 1), 2)
    
    # CO2 offset in vehicle equivalents (average car: 4.6 tons CO2/year)
    co2_offset_vehicles = int(co2_sequestration_annual / 4.6)
    
    # Canopy cover: starts at 20%, reaches 80% at maturity
    canopy_cover_percentage = round(min(20 + (years_active * 10), 85), 1)
    
    # Soil health index: improves over time (0-100 scale)
    soil_health_index = round(min(60 + (years_active * 5), 95), 1)
    
    # Biodiversity score: species count estimate
    biodiversity_score = int(min(30 + (area_hectares * 2) + (years_active * 10), 150))
    
    # Water retention: liters per hectare
    water_retention_capacity = round(area_hectares * 15000 * (canopy_cover_percentage / 100), 2)
    
    # Generate historical monthly data
    historical_data = generate_historical_data(months_active, area_hectares)
    
    return {
        "site_id": site_id,
        "area_hectares": area_hectares,
        "estimated_trees": estimated_trees,
        "estimated_biomass_tons": estimated_biomass_tons,
        "co2_sequestration_annual": co2_sequestration_annual,
        "co2_offset_vehicles": co2_offset_vehicles,
        "canopy_cover_percentage": canopy_cover_percentage,
        "soil_health_index": soil_health_index,
        "biodiversity_score": biodiversity_score,
        "water_retention_capacity": water_retention_capacity,
        "historical_data": historical_data
    }

def generate_historical_data(months: float, area_hectares: float) -> Dict[str, List]:
    """Generate month-by-month historical analytics data"""
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    num_months = min(int(months), 12)
    
    current_month = datetime.now().month - 1
    
    historical = {
        "months": [],
        "tree_count": [],
        "co2_sequestration": [],
        "canopy_cover": [],
        "soil_health": [],
        "biodiversity": []
    }
    
    for i in range(num_months):
        month_idx = (current_month - num_months + i + 1) % 12
        month_progress = (i + 1) / 12  # Progress in first year
        
        historical["months"].append(month_names[month_idx])
        historical["tree_count"].append(int(area_hectares * 600 * month_progress))
        historical["co2_sequestration"].append(round(area_hectares * 12.5 * month_progress, 2))
        historical["canopy_cover"].append(round(20 + (month_progress * 10), 1))
        historical["soil_health"].append(round(60 + (month_progress * 5), 1))
        historical["biodiversity"].append(int(30 + (area_hectares * 2 * month_progress)))
    
    return historical

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
    
    # Calculate area if not provided
    calculated_area = calculate_polygon_area_hectares(site.geometry)
    area_hectares = site.area_hectares if site.area_hectares else calculated_area
    
    if USE_SUPABASE:
        try:
            data = {
                "name": site.name,
                "description": site.description,
                "project_id": site.project_id,
                "geometry": json.dumps(site.geometry),  # Store as JSON string
                "area_hectares": area_hectares,
                "location_info": site.location_info
            }
            response = supabase.table("sites").insert(data).execute()
            created_site = response.data[0]
            
            # Calculate analytics for the new site
            analytics = calculate_environmental_analytics(
                created_site["id"],
                area_hectares,
                created_site.get("created_at")
            )
            
            return {
                "data": created_site,
                "analytics": analytics,
                "message": "Site created successfully"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # In-memory fallback
    current_time = datetime.now().isoformat()
    site_data = {
        "id": site_id_counter,
        "name": site.name,
        "description": site.description,
        "project_id": site.project_id,
        "geometry": json.dumps(site.geometry),  # Store as JSON string
        "area_hectares": area_hectares,
        "location_info": site.location_info,
        "created_at": current_time
    }
    sites_db[site_id_counter] = site_data
    
    # Calculate analytics for the new site
    analytics = calculate_environmental_analytics(
        site_id_counter,
        area_hectares,
        current_time
    )
    
    result = {
        "data": site_data,
        "analytics": analytics,
        "message": "Site created successfully"
    }
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

@app.get("/api/sites/{site_id}/analytics")
def get_site_analytics(site_id: int):
    """Get environmental analytics for a specific site"""
    
    # Get site data first
    site_data = None
    
    if USE_SUPABASE:
        try:
            response = supabase.table("sites").select("*").eq("id", site_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Site not found")
            site_data = response.data[0]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    else:
        # In-memory fallback
        if site_id not in sites_db:
            raise HTTPException(status_code=404, detail="Site not found")
        site_data = sites_db[site_id]
    
    # Calculate analytics
    area_hectares = site_data.get("area_hectares", 0)
    created_at = site_data.get("created_at")
    
    if area_hectares == 0:
        # Try to calculate from geometry
        try:
            geometry = json.loads(site_data["geometry"])
            area_hectares = calculate_polygon_area_hectares(geometry)
        except:
            area_hectares = 1.0  # Default fallback
    
    analytics = calculate_environmental_analytics(site_id, area_hectares, created_at)
    
    return analytics

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

