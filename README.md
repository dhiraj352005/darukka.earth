# Darukaa.Earth

Full-stack web application with FastAPI backend and React frontend.

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

The backend uses Python with FastAPI framework.

### Prerequisites
- Python 3.x

### Installed Dependencies
- FastAPI 0.141.1
- Uvicorn 0.53.0
- SQLAlchemy 2.0.54
- psycopg2-binary 2.9.13
- PyJWT 2.14.0

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
