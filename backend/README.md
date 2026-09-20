# Darukaa.Earth Backend API

FastAPI backend for the Darukaa.Earth climate tech platform with Supabase integration.

## Features

- ✅ User Authentication (Registration & Login)
- ✅ Conservation Projects Management
- ✅ Conservation Sites with Polygon Drawing
- ✅ GeoJSON Geometry Support
- ✅ Supabase Integration (with in-memory fallback)
- ✅ CORS Configuration for Vercel Frontend

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Required environment variables:

```env
# Supabase Configuration (Optional - will use in-memory storage if not provided)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Set Up Supabase Database (Optional)

If you want to use Supabase instead of in-memory storage:

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to the SQL Editor in your Supabase dashboard
3. Run the schema from `supabase_schema.sql`
4. Copy your project URL and anon key to `.env`

### 4. Run the Development Server

```bash
# From the backend directory
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication

- `POST /api/register` - Register new user
- `POST /api/login` - Login user

### Projects

- `GET /api/projects` - Get all projects
- `GET /api/projects/{id}` - Get project by ID
- `POST /api/projects` - Create new project
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

### Sites

- `GET /api/sites` - Get all conservation sites
- `GET /api/sites/{id}` - Get site by ID
- `POST /api/sites` - Create new site with polygon geometry
- `PUT /api/sites/{id}` - Update site
- `DELETE /api/sites/{id}` - Delete site

### Utility

- `GET /` - API root with status
- `GET /health` - Health check
- `GET /api/users` - List all users (dev only)
- `DELETE /api/users/clear` - Clear all users (dev only)

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Storage Modes

The backend supports two storage modes:

1. **Supabase** (Production) - When `SUPABASE_URL` and `SUPABASE_KEY` are configured
2. **In-Memory** (Development) - Automatic fallback when Supabase is not configured

The current storage mode is shown in:
- Root endpoint: `GET /`
- Health check: `GET /health`

## Creating a Site with Polygon

When drawing polygons on the map, the frontend will send a GeoJSON geometry like:

```json
{
  "name": "Conservation Site 1",
  "description": "Protected forest area",
  "project_id": 1,
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [77.5946, 12.9716],
        [77.5956, 12.9716],
        [77.5956, 12.9726],
        [77.5946, 12.9726],
        [77.5946, 12.9716]
      ]
    ]
  },
  "area_hectares": 25.5,
  "location_info": "Bangalore, India"
}
```

## Deployment

### Render

The backend is configured for Render deployment with:
- `render.yaml` - Service configuration
- `runtime.txt` - Python version (3.11.9)
- `requirements.txt` - Dependencies

### Environment Variables on Render

Set these in your Render dashboard:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SECRET_KEY`
- `PYTHON_VERSION=3.11.9`

## Development

### Run Tests

```bash
pytest
```

### Format Code

```bash
black .
```

### Type Checking

```bash
mypy main.py
```

## Security Notes

⚠️ **Important for Production:**

1. Remove the `/api/users/clear` endpoint
2. Implement proper password hashing (currently using plain text)
3. Implement JWT token validation
4. Add rate limiting
5. Enable HTTPS only
6. Validate all user inputs
7. Add proper error logging

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Supabase** - PostgreSQL database with PostGIS
- **Pydantic** - Data validation
- **python-dotenv** - Environment variable management
- **Uvicorn** - ASGI server

## License

MIT
