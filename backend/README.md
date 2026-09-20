# Darukaa.Earth Backend API

FastAPI backend with PostgreSQL + PostGIS for managing restoration and conservation projects with geographical data.

## Features

- ✅ **JWT Authentication** - Secure user registration and login
- ✅ **PostgreSQL + PostGIS** - Spatial database for geographical polygons
- ✅ **SQLAlchemy ORM** - Type-safe database models
- ✅ **Admin-Protected Endpoints** - Role-based access control
- ✅ **GeoJSON Support** - Standard format for geographical data
- ✅ **Automatic Database Initialization** - PostGIS extension auto-enabled

## Database Models

### User
- `id`: Primary key
- `email`: Unique email address
- `username`: Unique username
- `hashed_password`: Bcrypt hashed password
- `full_name`: Optional full name
- `is_active`: Active status
- `is_admin`: Administrator flag
- `created_at`, `updated_at`: Timestamps

### Project
- `id`: Primary key
- `name`: Project name
- `description`: Project description
- `owner_id`: Foreign key to User
- `status`: Project status (active, completed, archived)
- `created_at`, `updated_at`: Timestamps

### Site
- `id`: Primary key
- `name`: Site name
- `description`: Site description
- `project_id`: Foreign key to Project
- **`geometry`**: PostGIS POLYGON column (SRID 4326 - WGS84)
- `area_hectares`: Area in hectares
- `location_info`: Additional location information
- `created_at`, `updated_at`: Timestamps

## API Endpoints

### Authentication (`/auth`)

#### POST `/auth/register`
Register a new user
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword",
  "full_name": "John Doe",
  "is_admin": false
}
```

#### POST `/auth/login`
Login and get JWT token
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "is_admin": false
  }
}
```

#### GET `/auth/me`
Get current user info (requires authentication)

### Projects (`/projects`) - Admin Only

#### POST `/projects`
Create a new project
```json
{
  "name": "Mangrove Restoration Project",
  "description": "Restoring coastal mangroves",
  "status": "active"
}
```

#### GET `/projects`
Get all projects with their sites

#### GET `/projects/{project_id}`
Get a specific project with its sites

#### DELETE `/projects/{project_id}`
Delete a project and all its sites

### Sites (`/sites`) - Admin Only

#### POST `/sites`
Add a geographical site to a project
```json
{
  "name": "Site Alpha",
  "description": "First restoration site",
  "project_id": 1,
  "geometry": {
    "type": "Polygon",
    "coordinates": [[
      [77.5946, 12.9716],
      [77.5956, 12.9716],
      [77.5956, 12.9726],
      [77.5946, 12.9726],
      [77.5946, 12.9716]
    ]]
  },
  "area_hectares": 10,
  "location_info": "Near main road"
}
```

#### POST `/sites/bulk`
Add multiple sites at once (accepts an array of site objects)

#### GET `/sites`
Get all sites with GeoJSON geometry

#### GET `/sites/{site_id}`
Get a specific site

#### DELETE `/sites/{site_id}`
Delete a site

## Running the Server

### Development Mode

From the project root:
```bash
backend\venv\Scripts\uvicorn main:app --reload --app-dir backend
```

Or from the backend directory:
```bash
cd backend
..\backend\venv\Scripts\uvicorn main:app --reload
```

Or using Python:
```bash
cd backend
..\backend\venv\Scripts\python main.py
```

### Access API Documentation

Once the server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Root Info**: http://localhost:8000/

## Environment Variables

Required in `backend/.env`:
```
DATABASE_URL=postgresql://user:password@host:port/database
JWT_SECRET_KEY=your-secret-key-here
```

## Database Initialization

The application automatically:
1. Enables the PostGIS extension on startup
2. Creates all tables if they don't exist
3. Validates the database connection

## GeoJSON Format

Sites use standard GeoJSON for polygon geometry:

```json
{
  "type": "Polygon",
  "coordinates": [[
    [longitude, latitude],
    [longitude, latitude],
    [longitude, latitude],
    [longitude, latitude],
    [longitude, latitude]  // Close the polygon (first point repeated)
  ]]
}
```

**Note**: GeoJSON uses [longitude, latitude] order, not [latitude, longitude].

## Authentication

Protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your-token-here>
```

Admin-only endpoints additionally require `is_admin: true` in the user record.

## Tech Stack

- **FastAPI** 0.141.1 - Modern Python web framework
- **SQLAlchemy** 2.0.54 - SQL toolkit and ORM
- **PostgreSQL** - Primary database
- **PostGIS** - Spatial database extension
- **GeoAlchemy2** 0.20.0 - PostGIS integration for SQLAlchemy
- **Pydantic** - Data validation
- **python-jose** - JWT token handling
- **passlib** + **bcrypt** - Password hashing
- **Shapely** - Geometry manipulation
- **Uvicorn** - ASGI server

## Testing

Run the startup test:
```bash
backend\venv\Scripts\python backend\test_startup.py
```

This verifies:
- All imports work correctly
- Database connection is successful
- PostGIS extension is enabled
- Tables are created properly

## Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── database.py          # Database configuration and session management
├── models.py            # SQLAlchemy models (User, Project, Site)
├── schemas.py           # Pydantic schemas for validation
├── auth.py              # Authentication utilities (JWT, password hashing)
├── routes_auth.py       # Authentication endpoints
├── routes_projects.py   # Project management endpoints
├── routes_sites.py      # Site management endpoints
├── test_startup.py      # Startup verification script
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in git)
└── .env.example         # Environment template
```

## Troubleshooting

### Database Connection Issues

If you see "could not translate host name":
- Check your internet connection
- Verify the DATABASE_URL in `.env` is correct
- Ensure Supabase database is accessible
- Check firewall settings

### Import Errors

If you see module import errors:
```bash
backend\venv\Scripts\python -m pip install -r backend\requirements.txt
```

### PostGIS Extension Missing

If PostGIS is not available on your database, you'll need to enable it manually:
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

## Next Steps

1. Register an admin user via `/auth/register` with `is_admin: true`
2. Login to get a JWT token
3. Create projects via `/projects`
4. Add geographical sites to projects via `/sites`
5. Query projects and sites via GET endpoints

## License

Part of the Darukaa.Earth project.
