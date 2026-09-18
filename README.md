# 🌍 Darukaa.Earth

**A Full-Stack Restoration & Conservation Platform**

Darukaa.Earth is a comprehensive geospatial management platform for environmental restoration and conservation projects. It combines interactive mapping, spatial data management, and performance analytics to help organizations track and visualize their environmental impact.

[![CI/CD Pipeline](https://github.com/yourusername/darukaa.earth/workflows/Darukaa.Earth%20CI/CD%20Pipeline/badge.svg)](https://github.com/yourusername/darukaa.earth/actions)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-high-level-architecture)
- [Database Schema](#-database-schema)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Local Setup](#-local-setup-instructions)
- [CI/CD Pipeline](#-cicd-pipeline)
- [API Documentation](#-api-documentation)
- [Usage Guide](#-usage-guide)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### Core Functionality
- 🔐 **JWT Authentication** - Secure user registration and login
- 🗺️ **Interactive Mapping** - Full-screen Mapbox GL JS satellite view
- 📐 **Polygon Drawing** - Draw site boundaries directly on the map
- 💾 **Spatial Data Management** - PostgreSQL + PostGIS for geospatial data
- 📊 **Performance Analytics** - Highcharts-powered data visualization
- 👨‍💼 **Role-Based Access** - Admin controls for site management
- 🌐 **RESTful API** - Clean, documented endpoints

### Technical Features
- PostGIS geometry columns for storing map polygons
- GeoJSON format for frontend-backend communication
- Automatic PostGIS extension initialization
- Real-time site visualization on interactive maps
- Responsive design for desktop and mobile
- Pre-commit hooks for code quality

---

## 🏗️ High-Level Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │   React Frontend (Port 5173)                           │ │
│  │   • Login/Register UI                                  │ │
│  │   • Dashboard with Mapbox GL JS                        │ │
│  │   • Polygon Drawing Tools (Mapbox Draw)                │ │
│  │   • Highcharts Analytics Modal                         │ │
│  │   • Protected Routes (React Router)                    │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP/HTTPS
                            ↓ JWT Tokens
                            ↓ JSON/GeoJSON
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │   FastAPI Backend (Port 8000)                          │ │
│  │   • Authentication Endpoints (JWT)                     │ │
│  │   • Project Management API                             │ │
│  │   • Site Management API (GeoJSON)                      │ │
│  │   • CORS Middleware                                    │ │
│  │   • Pydantic Validation                                │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓ SQLAlchemy ORM
                            ↓ PostGIS Queries
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                        Data Layer                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │   PostgreSQL + PostGIS (Supabase)                      │ │
│  │   • Users Table (authentication)                       │ │
│  │   • Projects Table (project management)                │ │
│  │   • Sites Table (spatial data with GEOMETRY column)    │ │
│  │   • PostGIS Extension (spatial functions)              │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Architecture Principles

**1. Three-Tier Architecture**
- **Presentation Tier:** React frontend with Mapbox and Highcharts
- **Application Tier:** FastAPI REST API with business logic
- **Data Tier:** PostgreSQL database with PostGIS extension

**2. API-First Design**
- RESTful endpoints with clear resource naming
- JSON and GeoJSON for data interchange
- OpenAPI documentation auto-generated

**3. Security Layers**
- JWT tokens for stateless authentication
- Bcrypt password hashing with salt
- Role-based access control (RBAC)
- CORS configuration for frontend-backend communication

**4. Spatial Data Flow**

```
User draws polygon on map (Mapbox Draw)
    ↓
GeoJSON format {"type": "Polygon", "coordinates": [...]}
    ↓
Frontend sends POST /sites with GeoJSON
    ↓
Backend converts GeoJSON → Shapely Geometry
    ↓
Shapely Geometry → PostGIS GEOMETRY(POLYGON, 4326)
    ↓
Stored in PostgreSQL with spatial index
    ↓
Retrieved and converted back to GeoJSON for display
    ↓
Rendered as colored polygons on Mapbox map
```

---

## 🗄️ Database Schema

### Entity Relationship Diagram

```
┌─────────────────────────┐
│         Users           │
├─────────────────────────┤
│ id (PK)                 │
│ email (UNIQUE)          │
│ username (UNIQUE)       │
│ hashed_password         │
│ full_name               │
│ is_active               │
│ is_admin                │◄─────────┐
│ created_at              │          │
│ updated_at              │          │
└─────────────────────────┘          │
                                     │
                                     │ owns (1:N)
                                     │
┌─────────────────────────┐          │
│       Projects          │          │
├─────────────────────────┤          │
│ id (PK)                 │          │
│ name                    │          │
│ description             │          │
│ owner_id (FK)           │──────────┘
│ status                  │
│ created_at              │
│ updated_at              │◄─────────┐
└─────────────────────────┘          │
                                     │
                                     │ contains (1:N)
                                     │
┌─────────────────────────┐          │
│         Sites           │          │
├─────────────────────────┤          │
│ id (PK)                 │          │
│ name                    │          │
│ description             │          │
│ project_id (FK)         │──────────┘
│ geometry (GEOMETRY)     │ ◄── PostGIS POLYGON
│ area_hectares           │
│ location_info           │
│ created_at              │
│ updated_at              │
└─────────────────────────┘
```

### Table Definitions

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

**Purpose:** Store user authentication and authorization data  
**Security:** Passwords hashed with bcrypt (never stored in plain text)  
**Relationships:** One user can own multiple projects

#### Projects Table
```sql
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id INTEGER NOT NULL REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_projects_owner ON projects(owner_id);
CREATE INDEX idx_projects_status ON projects(status);
```

**Purpose:** Organize sites into restoration/conservation projects  
**Status Values:** 'active', 'completed', 'archived'  
**Relationships:** Belongs to one user, contains multiple sites

#### Sites Table (with PostGIS)
```sql
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE sites (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    geometry GEOMETRY(POLYGON, 4326) NOT NULL,  -- PostGIS column
    area_hectares INTEGER,
    location_info TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_sites_project ON sites(project_id);
CREATE INDEX idx_sites_geometry ON sites USING GIST(geometry);  -- Spatial index
```

**Purpose:** Store geographical site boundaries as polygons  
**Geometry Column:**
- Type: POLYGON (closed polygons only)
- SRID: 4326 (WGS84 - standard GPS coordinates)
- Indexed with GIST for fast spatial queries

**Spatial Features:**
- ST_Area() - Calculate polygon area
- ST_Contains() - Check if point is inside polygon
- ST_Intersects() - Find overlapping polygons
- ST_Distance() - Measure distances between sites

### Cascade Delete Behavior

```
Delete Project → Automatically deletes all associated Sites
Delete User → Project ownership must be reassigned first
```

---

## Project Structure

```
darukaa.earth/
├── backend/              # FastAPI Python backend
│   ├── venv/            # Python virtual environment
│   ├── main.py          # FastAPI application entry point
│   ├── requirements.txt # Python dependencies
│   └── .env.example     # Environment variables template
├── frontend/            # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── ...
│   ├── .husky/         # Git hooks
│   ├── package.json
│   ├── vite.config.js
│   └── eslint.config.js
├── .gitignore
└── README.md
```

## Backend Setup

The backend uses Python with FastAPI framework and PostgreSQL + PostGIS for spatial data.

### Prerequisites
- Python 3.x
- PostgreSQL with PostGIS extension (using Supabase)

### Installed Dependencies
- FastAPI 0.141.1 - Web framework
- Uvicorn 0.53.0 - ASGI server
- SQLAlchemy 2.0.54 - ORM
- psycopg2-binary 2.9.13 - PostgreSQL adapter
- GeoAlchemy2 0.20.0 - PostGIS integration
- Shapely 2.1.2 - Geometry manipulation
- JWT & Auth libraries

### Features
✅ JWT Authentication with user registration and login  
✅ PostgreSQL + PostGIS for spatial data  
✅ SQLAlchemy models: User, Project, Site  
✅ PostGIS Geometry column for storing map polygons  
✅ Admin-protected endpoints for projects and sites  
✅ GeoJSON support for geographical data  

### Running the Backend
```bash
cd backend
# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Run the server
python main.py
# Or with uvicorn directly:
uvicorn main:app --reload
```

The backend API will be available at `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### API Endpoints

**Authentication** (`/auth`):
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info

**Projects** (`/projects`) - Admin only:
- `POST /projects` - Create project
- `GET /projects` - List all projects with sites
- `GET /projects/{id}` - Get specific project
- `DELETE /projects/{id}` - Delete project

**Sites** (`/sites`) - Admin only:
- `POST /sites` - Add geographical site (polygon)
- `POST /sites/bulk` - Add multiple sites
- `GET /sites` - List all sites
- `GET /sites/{id}` - Get specific site
- `DELETE /sites/{id}` - Delete site

📖 **See `backend/README.md` for detailed API documentation.**

## Frontend Setup

The frontend uses React with Vite as the build tool.

### Prerequisites
- Node.js 18+ and npm

### Installation

```bash
cd frontend
npm install
```

### Running the Frontend
```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Pre-commit Hooks

The frontend is configured with Husky and lint-staged to automatically format and lint code before commits:

- **Prettier**: Formats code automatically
- **ESLint**: Lints and fixes JavaScript/JSX files

The pre-commit hook will run automatically when you commit changes in the frontend directory.

## Development Workflow

1. **Start the backend server:**
   ```bash
   cd backend
   venv\Scripts\activate  # Windows
   python main.py
   ```
   Backend runs on `http://localhost:8000`

2. **Start the frontend dev server:**
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend runs on `http://localhost:5173`

3. **Make changes and commit:**
   - The pre-commit hook will automatically format and lint your code
   - Prettier formats all files
   - ESLint checks JavaScript/JSX files

## Available Scripts

### Backend
- `python main.py` - Start the FastAPI server
- `uvicorn main:app --reload` - Start with auto-reload

### Frontend
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Installed Dependencies

### Backend
- FastAPI 0.141.1
- Uvicorn 0.53.0
- SQLAlchemy 2.0.54
- psycopg2-binary 2.9.13
- PyJWT 2.14.0

### Frontend
- React 18.3.1
- Vite 6.0.7
- ESLint 9.17.0
- Prettier 3.4.2
- Husky 9.1.7
- lint-staged 15.2.11

## Git

This repository is initialized with Git. Remember to:
- Add files: `git add <files>`
- Commit changes: `git commit -m "message"`
- The pre-commit hook will automatically format and lint committed files

## Notes

- Python virtual environment: `backend/venv/`
- Frontend dependencies: `frontend/node_modules/`
- All configuration files are set up and ready to use
- Pre-commit hooks will run automatically on git commits
- Backend API docs available at `http://localhost:8000/docs`

## Next Steps

1. Copy `backend/.env.example` to `backend/.env` and configure your environment
2. Set up your PostgreSQL database
3. Create database models in the backend
4. Build out your API endpoints
5. Connect the frontend to the backend API

## 🛠️ Tech Stack

### Backend
- **FastAPI** 0.141.1 - Modern Python web framework
- **PostgreSQL** - Primary database (hosted on Supabase)
- **PostGIS** - Spatial database extension for geometry operations
- **SQLAlchemy** 2.0.54 - SQL toolkit and ORM
- **GeoAlchemy2** 0.20.0 - PostGIS integration for SQLAlchemy
- **Shapely** 2.1.2 - Geometry manipulation and validation
- **python-jose** 3.5.0 - JWT token encoding/decoding
- **passlib** 1.7.4 - Password hashing with bcrypt
- **Uvicorn** 0.53.0 - ASGI server

### Frontend
- **React** 18.3.1 - UI library
- **Vite** 6.0.7 - Build tool and dev server
- **Mapbox GL JS** - Interactive mapping library
- **Mapbox Draw** - Polygon drawing plugin
- **Highcharts** - Data visualization library
- **Axios** - HTTP client for API calls
- **React Router** - Client-side routing
- **ESLint** + **Prettier** - Code quality tools

### DevOps
- **GitHub Actions** - CI/CD pipeline
- **Husky** - Git hooks for code quality
- **lint-staged** - Run linters on staged files

---

## 📋 Prerequisites

Before setting up the project, ensure you have:

- **Node.js** 18+ and npm
- **Python** 3.11+ and pip
- **Git** for version control
- **PostgreSQL** database with PostGIS (we use Supabase)
- **Mapbox account** for map token (free tier available)
- **Code editor** (VS Code recommended)

### Account Setup

1. **Supabase Account** (for PostgreSQL + PostGIS):
   - Sign up at https://supabase.com
   - Create a new project
   - Enable PostGIS extension in SQL editor:
     ```sql
     CREATE EXTENSION IF NOT EXISTS postgis;
     ```
   - Copy connection string from Project Settings → Database

2. **Mapbox Account** (for maps):
   - Sign up at https://www.mapbox.com
   - Go to Account → Tokens
   - Create a new token or use default public token
   - Copy the access token

---

## 🚀 Local Setup Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/darukaa.earth.git
cd darukaa.earth
```

### Step 2: Backend Setup

#### 2.1 Create Python Virtual Environment

```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 2.2 Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2.3 Configure Environment Variables

Create `backend/.env` file:

```env
DATABASE_URL=postgresql://user:password@host:port/database
JWT_SECRET_KEY=your-secret-key-here
```

**Important:** 
- Replace with your actual Supabase connection string
- Use a strong, random JWT secret key
- Never commit `.env` to version control

#### 2.4 Verify Backend Setup

```bash
python test_startup.py
```

Expected output:
```
Testing imports...
✓ All imports successful

Testing database connection...
✓ Database connected: PostgreSQL 15.x...

Initializing PostGIS...
✓ PostGIS extension initialized successfully

Creating database tables...
✓ Database tables created successfully

✅ ALL TESTS PASSED!
```

### Step 3: Frontend Setup

#### 3.1 Install Node Dependencies

```bash
cd ../frontend
npm install
```

#### 3.2 Configure Environment Variables

Create `frontend/.env` file:

```env
VITE_MAPBOX_TOKEN=your-mapbox-token-here
VITE_API_URL=http://localhost:8000
```

**Important:**
- Replace with your actual Mapbox access token
- Keep VITE_API_URL pointing to local backend

#### 3.3 Verify Frontend Setup

```bash
npm run lint
npm run build
```

### Step 4: Run the Application

#### 4.1 Start Backend Server

Terminal 1:
```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
python main.py
```

Backend runs on **http://localhost:8000**

Verify:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

#### 4.2 Start Frontend Dev Server

Terminal 2:
```bash
cd frontend
npm run dev
```

Frontend runs on **http://localhost:5173**

### Step 5: Create First Admin User

#### Option 1: Using API Docs (Recommended)

1. Open http://localhost:8000/docs
2. Navigate to POST /auth/register
3. Click "Try it out"
4. Enter:
   ```json
   {
     "email": "admin@example.com",
     "username": "admin",
     "password": "SecurePass123!",
     "full_name": "Admin User",
     "is_admin": true
   }
   ```
5. Click "Execute"

#### Option 2: Using Frontend

1. Open http://localhost:5173
2. Click "Register" tab
3. Fill in the form
4. **Check "Register as Administrator"**
5. Click "Register"

### Step 6: Login and Explore

1. Navigate to http://localhost:5173
2. Login with your credentials
3. You'll be redirected to the dashboard
4. Explore features:
   - View the interactive map
   - Draw polygons (admin only)
   - Click on sites to view analytics

---

## 🔄 CI/CD Pipeline

### Pipeline Overview

The GitHub Actions CI/CD pipeline automatically runs on every push to the `main` branch and on all pull requests. It ensures code quality and prevents broken code from being merged.

### Pipeline Structure

```yaml
Pipeline: Darukaa.Earth CI/CD
├── Job 1: Frontend Checks (parallel)
│   ├── Checkout code
│   ├── Setup Node.js 18
│   ├── Install dependencies (npm ci)
│   ├── Run ESLint (npm run lint)
│   ├── Build frontend (npm run build)
│   └── Upload build artifacts
│
├── Job 2: Backend Tests (parallel)
│   ├── Checkout code
│   ├── Setup Python 3.11
│   ├── Install dependencies (pip install)
│   ├── Run import tests
│   └── Run syntax checks (py_compile)
│
└── Job 3: All Checks (depends on 1 & 2)
    └── Verify all jobs passed
```

### Pipeline Configuration

**Location:** `.github/workflows/main.yml`

**Triggers:**
```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

**Jobs Explained:**

#### 1. Frontend Checks Job

**Purpose:** Validate frontend code quality and build

**Steps:**
1. **Checkout code** - Gets latest code from repository
2. **Setup Node.js** - Installs Node.js 18 with npm caching
3. **Install dependencies** - Runs `npm ci` (clean install)
4. **Run ESLint** - Checks code style and catches errors
   - Fails if linting errors found
   - Validates React, JavaScript, JSX code
5. **Build frontend** - Runs `npm run build`
   - Ensures production build works
   - Catches build-time errors
6. **Upload artifacts** - Saves build output
   - Retained for 7 days
   - Can be downloaded for deployment

**Why it matters:**
- Catches syntax errors before merge
- Enforces code style consistency
- Verifies production build succeeds

#### 2. Backend Tests Job

**Purpose:** Validate backend code integrity

**Steps:**
1. **Checkout code** - Gets latest code
2. **Setup Python** - Installs Python 3.11 with pip caching
3. **Install dependencies** - Runs `pip install -r requirements.txt`
4. **Run import tests** - Verifies all modules import correctly
   - Tests: models, schemas, auth utilities
   - Catches missing dependencies
   - Validates module structure
5. **Run syntax checks** - Compiles all Python files
   - Uses `python -m py_compile`
   - Catches syntax errors
   - Validates Python code structure

**Why it matters:**
- Ensures all dependencies are listed
- Catches import errors early
- Validates Python syntax

#### 3. All Checks Job

**Purpose:** Final status gate

**Dependencies:** Requires both frontend-checks and backend-tests to pass

**Why it matters:**
- Single status check for branch protection
- Clear pass/fail indicator
- Prevents merge if any job fails

### Running Pipeline Locally

Before pushing, you can run the same checks locally:

#### Frontend Checks
```bash
cd frontend
npm ci
npm run lint
npm run build
```

#### Backend Tests
```bash
cd backend
pip install -r requirements.txt

# Test imports
python -c "from models import User, Project, Site; print('✓ Imports OK')"

# Test syntax
python -m py_compile main.py database.py models.py
```

### Pipeline Status Badge

Add to your README:
```markdown
[![CI/CD Pipeline](https://github.com/yourusername/darukaa.earth/workflows/Darukaa.Earth%20CI/CD%20Pipeline/badge.svg)](https://github.com/yourusername/darukaa.earth/actions)
```

### Branch Protection Rules

**Recommended settings:**

1. Go to: Settings → Branches → Branch protection rules
2. Add rule for `main` branch:
   - ☑ Require status checks to pass before merging
   - ☑ Require branches to be up to date before merging
   - Select: `All Checks Passed`
   - ☑ Require linear history
   - ☑ Include administrators

**Result:** No code can be merged to main without passing all CI checks.

### Continuous Deployment (Future)

The pipeline can be extended for automatic deployment:

```yaml
deploy-production:
  needs: [frontend-checks, backend-tests]
  if: github.ref == 'refs/heads/main'
  steps:
    - name: Deploy to production
      run: |
        # Deploy frontend to Vercel/Netlify
        # Deploy backend to AWS/Heroku
```

---

## 📚 API Documentation

### Interactive Documentation

Once the backend is running, access:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Authentication Endpoints

#### POST /auth/register
Register a new user

**Request:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "is_admin": false
}
```

**Response:** 201 Created
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_admin": false,
  "created_at": "2026-09-18T12:00:00Z"
}
```

#### POST /auth/login
Login and receive JWT token

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:** 200 OK
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

#### GET /auth/me
Get current user information

**Headers:** `Authorization: Bearer <token>`

**Response:** 200 OK
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "is_admin": false
}
```

### Project Endpoints (Admin Only)

#### POST /projects
Create a new project

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "name": "Coastal Mangrove Restoration",
  "description": "Restoring mangrove forests in coastal areas",
  "status": "active"
}
```

**Response:** 201 Created

#### GET /projects
List all projects with their sites

**Headers:** `Authorization: Bearer <token>`

**Response:** 200 OK (array of projects with nested sites)

### Site Endpoints (Admin Only)

#### POST /sites
Create a geographical site

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "name": "Site Alpha",
  "description": "Primary restoration area",
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
  "area_hectares": 100,
  "location_info": "Near coastal highway"
}
```

**Response:** 201 Created

#### GET /sites
List all sites

**Headers:** `Authorization: Bearer <token>`

**Response:** 200 OK (array of sites with GeoJSON geometry)

### Error Responses

All endpoints return structured error responses:

**401 Unauthorized:**
```json
{
  "detail": "Could not validate credentials"
}
```

**403 Forbidden:**
```json
{
  "detail": "The user doesn't have enough privileges"
}
```

**404 Not Found:**
```json
{
  "detail": "Project with id 99 not found"
}
```

---

## 📖 Usage Guide

### For Regular Users

1. **Register and Login**
   - Navigate to http://localhost:5173
   - Register with your email
   - Login to access dashboard

2. **View Map**
   - See all project sites as colored polygons
   - Navigate with mouse or controls
   - Zoom in/out with scroll wheel

3. **View Site Analytics**
   - Click on any site polygon
   - Analytics modal opens
   - View performance charts and statistics

### For Administrators

All regular user features, plus:

1. **Draw New Sites**
   - Click polygon tool (top-left)
   - Click on map to place vertices
   - Double-click to complete polygon
   - Click "Save Site" button
   - Enter site details

2. **Manage Projects**
   - Use API endpoints to create projects
   - Assign sites to projects
   - Update project status

3. **Site Operations**
   - Create single or multiple sites
   - Delete sites when needed
   - View all sites across projects

---

## 📂 Project Structure

```
darukaa.earth/
├── .github/
│   └── workflows/
│       └── main.yml              # CI/CD pipeline configuration
│
├── backend/
│   ├── venv/                     # Python virtual environment
│   ├── .env                      # Environment variables (not in git)
│   ├── .env.example              # Environment template
│   ├── main.py                   # FastAPI application entry
│   ├── database.py               # Database configuration
│   ├── models.py                 # SQLAlchemy models
│   ├── schemas.py                # Pydantic schemas
│   ├── auth.py                   # Authentication utilities
│   ├── routes_auth.py            # Auth endpoints
│   ├── routes_projects.py        # Project endpoints
│   ├── routes_sites.py           # Site endpoints
│   ├── test_startup.py           # Startup verification
│   ├── requirements.txt          # Python dependencies
│   └── README.md                 # Backend documentation
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Login.jsx         # Authentication UI
│   │   │   ├── Login.css
│   │   │   ├── Dashboard.jsx     # Main dashboard
│   │   │   ├── Dashboard.css
│   │   │   ├── MapView.jsx       # Mapbox integration
│   │   │   ├── MapView.css
│   │   │   ├── SiteAnalytics.jsx # Highcharts modal
│   │   │   └── SiteAnalytics.css
│   │   ├── context/
│   │   │   └── AuthContext.jsx   # Auth state management
│   │   ├── services/
│   │   │   └── api.js            # API client
│   │   ├── App.jsx               # Router setup
│   │   ├── App.css
│   │   ├── main.jsx              # Entry point
│   │   └── index.css
│   ├── .env                      # Environment variables (not in git)
│   ├── .husky/                   # Git hooks
│   ├── package.json
│   ├── vite.config.js
│   ├── eslint.config.js
│   └── README.md                 # Frontend documentation
│
├── .gitignore
└── README.md                     # This file
```

---

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Run tests locally**
   ```bash
   # Frontend
   cd frontend && npm run lint && npm run build
   
   # Backend
   cd backend && python test_startup.py
   ```
5. **Commit with meaningful messages**
   ```bash
   git commit -m "feat: add new feature"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a Pull Request**
8. **Wait for CI/CD checks to pass**
9. **Address review comments**
10. **Merge when approved**

### Code Style Guidelines

**Python (Backend):**
- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Keep functions focused and small

**JavaScript/React (Frontend):**
- Use functional components
- Follow React hooks best practices
- Use meaningful variable names
- Add comments for complex logic

**Git Commit Messages:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test updates
- `chore:` Build/config changes

### Pre-commit Hooks

The project uses Husky and lint-staged:
- Automatically runs on `git commit`
- Formats code with Prettier
- Lints code with ESLint
- Prevents committing broken code

---

## 📄 License

This project is part of the Darukaa.Earth initiative for environmental conservation and restoration.

---

## 🙏 Acknowledgments

- **Mapbox** for interactive mapping
- **Highcharts** for data visualization
- **PostGIS** for spatial database capabilities
- **FastAPI** for modern Python web framework
- **React** for powerful UI development
- **Supabase** for managed PostgreSQL hosting

---

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review API docs at `/docs` endpoint

---

**Built with ❤️ for environmental conservation worldwide** 🌍🌱


---

## 🚀 Deployment Guide - Vercel

### **Frontend Deployment (Vercel)**

#### **Option 1: Deploy via Vercel Dashboard (सर्वात सोपा मार्ग)**

1. **Vercel वर Login करा**
   - Visit: https://vercel.com
   - "Sign Up" किंवा "Login" वर क्लिक करा
   - GitHub account वापरून login करा

2. **New Project तयार करा**
   - Dashboard वर "Add New..." → "Project" वर क्लिक करा
   - GitHub repositories ची list दिसेल
   - `darukka.earth` repository शोधा आणि "Import" वर क्लिक करा

3. **Project Configuration**
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

4. **Environment Variables Add करा**
   - "Environment Variables" section मध्ये जा
   - खालील variables add करा:
   
   | Name | Value |
   |------|-------|
   | `VITE_MAPBOX_TOKEN` | तुमचा Mapbox token |
   | `VITE_API_URL` | तुमचा backend URL (deployed) |

5. **Deploy वर क्लिक करा**
   - 2-3 मिनिटे वाट पहा
   - Build complete झाल्यावर तुम्हाला URL मिळेल (उदा: `https://darukaa-earth.vercel.app`)

#### **Option 2: Deploy via Vercel CLI**

```bash
# Vercel CLI Install करा
npm install -g vercel

# Frontend folder मध्ये जा
cd frontend

# Deploy command run करा
vercel

# Production deploy साठी
vercel --prod
```

#### **Step-by-step CLI Prompts:**
```
? Set up and deploy "~/darukaa.earth/frontend"? [Y/n] Y
? Which scope do you want to deploy to? Your Name
? Link to existing project? [y/N] n
? What's your project's name? darukaa-earth
? In which directory is your code located? ./
? Want to modify these settings? [y/N] n
```

---

### **Backend Deployment Options**

Backend साठी Vercel free tier फारसा योग्य नाही (Serverless Functions limitations). तुमच्याकडे options आहेत:

#### **Option 1: Render (Free Tier Available) - Recommended**

1. **Render.com वर Account तयार करा**
   - Visit: https://render.com
   - GitHub वापरून sign up करा

2. **New Web Service तयार करा**
   - Dashboard → "New" → "Web Service"
   - GitHub repo connect करा

3. **Configuration:**
   ```
   Name: darukaa-earth-backend
   Region: Singapore (nearest to India)
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **Environment Variables:**
   - `DATABASE_URL` - तुमचा Supabase connection string
   - `JWT_SECRET_KEY` - तुमची secret key
   - `PORT` - 8000

5. **Deploy वर क्लिक करा**

#### **Option 2: Railway (Free $5 Credit)**

1. **Railway.app वर जा**
   - Visit: https://railway.app
   - GitHub वापरून sign up करा

2. **New Project → Deploy from GitHub repo**
   - `darukka.earth` select करा

3. **Configuration:**
   ```
   Root Directory: backend
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **Environment Variables add करा**

#### **Option 3: Python Anywhere (Free Tier)**

1. **Account Create** - https://www.pythonanywhere.com
2. **Web App Setup** - Manual configuration करावा लागेल
3. **WSGI Configuration** - FastAPI ASGI साठी setup

---

### **Environment Variables सुरक्षित कसे ठेवायचे**

#### **GitHub Secrets (CI/CD साठी)**
1. GitHub repo → Settings → Secrets and variables → Actions
2. "New repository secret" वर क्लिक करा
3. Add:
   - `DATABASE_URL`
   - `JWT_SECRET_KEY`
   - `VITE_MAPBOX_TOKEN`

#### **Production Environment Variables**

**Frontend (.env.production):**
```env
VITE_MAPBOX_TOKEN=pk.your-mapbox-token
VITE_API_URL=https://your-backend-url.render.com
```

**Backend (.env on Render/Railway):**
```env
DATABASE_URL=postgresql://user:pass@host:port/db
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
CORS_ORIGINS=https://darukaa-earth.vercel.app
```

---

### **Post-Deployment Checklist**

✅ **1. Frontend Deployed Successfully**
- Vercel dashboard मध्ये green status दिसतो
- Live URL वर website उघडतो
- Console मध्ये errors नाहीत

✅ **2. Backend Deployed Successfully**
- Render/Railway logs मध्ये "Application startup complete" दिसतं
- `/docs` endpoint कार्य करतो
- Health check API response देतो

✅ **3. Database Connection**
- Backend logs मध्ये database connection errors नाहीत
- Supabase dashboard मध्ये connections दिसतात

✅ **4. CORS Configuration**
- Backend मध्ये frontend URL allowed आहे
- API calls console मध्ये CORS errors नाहीत

✅ **5. Environment Variables**
- सर्व secrets properly configured आहेत
- `.env` files git मध्ये commit केलेल्या नाहीत

✅ **6. API Integration**
- Frontend → Backend API calls work करतात
- Login/Register functionality चालू आहे
- Map loads properly

---

### **Common Issues & Solutions**

#### **❌ Issue: Build Failed on Vercel**
**Solution:**
```bash
# Local build test करा
cd frontend
npm run build

# Error logs वाचा आणि fix करा
```

#### **❌ Issue: CORS Error**
**Solution:** Backend `main.py` मध्ये:
```python
origins = [
    "https://darukaa-earth.vercel.app",  # तुमचा Vercel URL
    "http://localhost:5173",  # Development
]
```

#### **❌ Issue: Environment Variables Not Loading**
**Solution:**
- Vercel dashboard मधून variables double-check करा
- Rebuild trigger करा: Deployments → ... → Redeploy

#### **❌ Issue: API 502/504 Timeout**
**Solution:**
- Backend logs check करा
- Database connection verify करा
- Cold start delay असू शकतो (first request slow)

---

### **Custom Domain Setup (Optional)**

#### **Vercel मध्ये Custom Domain Add करायचं:**

1. Vercel Project → Settings → Domains
2. Domain name enter करा (उदा: `darukaa.earth`)
3. DNS records update करा:
   ```
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   ```
4. SSL automatic setup होईल (Let's Encrypt)

---

### **Performance Optimization Tips**

1. **Frontend Optimization:**
   - Image optimization (WebP format वापरा)
   - Lazy loading for components
   - Bundle size minimize करा

2. **Backend Optimization:**
   - Database connection pooling enable करा
   - API response caching add करा
   - Keep-alive connections वापरा

3. **Monitoring Setup:**
   - Vercel Analytics enable करा
   - Sentry error tracking add करा
   - Database performance monitor करा

---

### **Quick Deployment Commands**

```bash
# Frontend deploy (production)
cd frontend
vercel --prod

# Check deployment status
vercel ls

# View logs
vercel logs

# Frontend environment variables set करा
vercel env add VITE_MAPBOX_TOKEN production

# Backend locally test करा deployment साठी
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

### **Deployment URLs Structure**

```
Frontend (Vercel):
Production: https://darukaa-earth.vercel.app
Preview: https://darukaa-earth-git-feature-yourname.vercel.app

Backend (Render):
Production: https://darukaa-earth-backend.onrender.com
API Docs: https://darukaa-earth-backend.onrender.com/docs

Database (Supabase):
Dashboard: https://app.supabase.com/project/your-project-id
Connection: postgres://...pooler.supabase.com:6543/postgres
```

---

### **Need Help?**

तुम्हाला deploy करतांना काही अडचण आली तर:

1. **Vercel Documentation:** https://vercel.com/docs
2. **Render Documentation:** https://render.com/docs
3. **GitHub Issues:** Create issue on repo
4. **Discord/Slack:** Community support

**Good Luck with Deployment! 🚀**

