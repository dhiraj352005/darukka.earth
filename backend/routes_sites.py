from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import shape, mapping
import json

from database import get_db
from models import User, Project, Site
from schemas import SiteCreate, SiteResponse
from auth import get_current_admin_user

router = APIRouter(prefix="/sites", tags=["Sites"])


@router.post("/", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
def create_site(
    site_data: SiteCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Add a geographical site (polygon) to a project (Admin only)
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == site_data.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {site_data.project_id} not found"
        )
    
    try:
        # Convert GeoJSON to Shapely geometry
        geom = shape(site_data.geometry)
        
        # Create new site with PostGIS geometry
        new_site = Site(
            name=site_data.name,
            description=site_data.description,
            project_id=site_data.project_id,
            geometry=from_shape(geom, srid=4326),
            area_hectares=site_data.area_hectares,
            location_info=site_data.location_info
        )
        
        db.add(new_site)
        db.commit()
        db.refresh(new_site)
        
        # Convert geometry back to GeoJSON for response
        geom_response = to_shape(new_site.geometry)
        geojson = mapping(geom_response)
        
        return {
            "id": new_site.id,
            "name": new_site.name,
            "description": new_site.description,
            "project_id": new_site.project_id,
            "geometry": json.dumps(geojson),
            "area_hectares": new_site.area_hectares,
            "location_info": new_site.location_info,
            "created_at": new_site.created_at,
            "updated_at": new_site.updated_at
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid geometry data: {str(e)}"
        )


@router.post("/bulk", response_model=List[SiteResponse], status_code=status.HTTP_201_CREATED)
def create_multiple_sites(
    sites_data: List[SiteCreate],
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Add multiple geographical sites (polygons) to projects (Admin only)
    """
    created_sites = []
    
    for site_data in sites_data:
        # Verify project exists
        project = db.query(Project).filter(Project.id == site_data.project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {site_data.project_id} not found"
            )
        
        try:
            # Convert GeoJSON to Shapely geometry
            geom = shape(site_data.geometry)
            
            # Create new site with PostGIS geometry
            new_site = Site(
                name=site_data.name,
                description=site_data.description,
                project_id=site_data.project_id,
                geometry=from_shape(geom, srid=4326),
                area_hectares=site_data.area_hectares,
                location_info=site_data.location_info
            )
            
            db.add(new_site)
            db.flush()  # Flush to get the ID without committing
            
            # Convert geometry back to GeoJSON for response
            geom_response = to_shape(new_site.geometry)
            geojson = mapping(geom_response)
            
            site_response = {
                "id": new_site.id,
                "name": new_site.name,
                "description": new_site.description,
                "project_id": new_site.project_id,
                "geometry": json.dumps(geojson),
                "area_hectares": new_site.area_hectares,
                "location_info": new_site.location_info,
                "created_at": new_site.created_at,
                "updated_at": new_site.updated_at
            }
            created_sites.append(site_response)
        
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid geometry data for site '{site_data.name}': {str(e)}"
            )
    
    db.commit()
    return created_sites


@router.get("/", response_model=List[SiteResponse])
def get_all_sites(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all sites (Admin only)
    """
    sites = db.query(Site).all()
    
    result = []
    for site in sites:
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
        result.append(site_dict)
    
    return result


@router.get("/{site_id}", response_model=SiteResponse)
def get_site(
    site_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific site (Admin only)
    """
    site = db.query(Site).filter(Site.id == site_id).first()
    
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Site with id {site_id} not found"
        )
    
    # Convert PostGIS geometry to GeoJSON
    geom = to_shape(site.geometry)
    geojson = mapping(geom)
    
    return {
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


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_site(
    site_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a site (Admin only)
    """
    site = db.query(Site).filter(Site.id == site_id).first()
    
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Site with id {site_id} not found"
        )
    
    db.delete(site)
    db.commit()
    
    return None
