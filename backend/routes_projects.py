from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import shape, mapping
from shapely import wkt
import json

from database import get_db
from models import User, Project, Site
from schemas import ProjectCreate, ProjectResponse, ProjectWithSites, SiteCreate, SiteResponse
from auth import get_current_admin_user

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project (Admin only)
    """
    new_project = Project(
        name=project_data.name,
        description=project_data.description,
        status=project_data.status,
        owner_id=current_user.id
    )
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    return new_project


@router.get("/", response_model=List[ProjectWithSites])
def get_all_projects(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all projects with their sites (Admin only)
    """
    projects = db.query(Project).all()
    
    # Convert geometry to GeoJSON for each site
    result = []
    for project in projects:
        project_dict = {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "owner_id": project.owner_id,
            "status": project.status,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "sites": []
        }
        
        for site in project.sites:
            # Convert PostGIS geometry to GeoJSON
            geom = to_shape(site.geometry)
            geojson = mapping(geom)
            
            site_dict = {
                "id": site.id,
                "name": site.name,
                "description": site.description,
                "project_id": site.project_id,
                "geometry": json.dumps(geojson),
                "area_hectares": site.area_hectares,
                "location_info": site.location_info,
                "created_at": site.created_at,
                "updated_at": site.updated_at
            }
            project_dict["sites"].append(site_dict)
        
        result.append(project_dict)
    
    return result


@router.get("/{project_id}", response_model=ProjectWithSites)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific project with its sites (Admin only)
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    # Convert geometry to GeoJSON for each site
    project_dict = {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "owner_id": project.owner_id,
        "status": project.status,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "sites": []
    }
    
    for site in project.sites:
        # Convert PostGIS geometry to GeoJSON
        geom = to_shape(site.geometry)
        geojson = mapping(geom)
        
        site_dict = {
            "id": site.id,
            "name": site.name,
            "description": site.description,
            "project_id": site.project_id,
            "geometry": json.dumps(geojson),
            "area_hectares": site.area_hectares,
            "location_info": site.location_info,
            "created_at": site.created_at,
            "updated_at": site.updated_at
        }
        project_dict["sites"].append(site_dict)
    
    return project_dict


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a project and all its sites (Admin only)
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    db.delete(project)
    db.commit()
    
    return None
