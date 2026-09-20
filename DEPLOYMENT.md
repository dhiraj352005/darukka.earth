# Darukaa.Earth Deployment Guide

## 🚀 Production Deployment Setup

### Backend Deployment (Render)

1. **Deploy to Render:**
   - Connect your GitHub repository to Render
   - Create a new Web Service
   - Set the following:
     - **Build Command:** `pip install -r backend/requirements.txt`
     - **Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
     - **Root Directory:** Leave as root or set to `backend`

2. **Note your Render URL:**
   - After deployment, Render will provide a URL like: `https://darukaa-earth-api.onrender.com`
   - Copy this URL - you'll need it for the frontend configuration

### Frontend Deployment (Vercel)

1. **Set Environment Variable in Vercel:**
   - Go to your Vercel project dashboard
   - Navigate to: **Settings → Environment Variables**
   - Add the following variable:
     ```
     Name: VITE_API_BASE_URL
     Value: https://your-backend-url.onrender.com
     ```
     ⚠️ **Important:** Replace `your-backend-url.onrender.com` with your actual Render backend URL

2. **Redeploy:**
   - After adding the environment variable, trigger a new deployment
   - You can do this by pushing a new commit or using Vercel's "Redeploy" button

### Verify CORS Configuration

The backend is already configured to accept requests from:
- `https://darukka-earth-bj6a.vercel.app` (your production frontend)
- `http://localhost:5173` (local development)
- All other origins (`*`) for flexibility

If you want to restrict CORS to only your domains, update `backend/main.py`:

```python
allow_origins=[
    "https://darukka-earth-bj6a.vercel.app",
    "http://localhost:5173",
]
```

## 🧪 Testing the Setup

### Test Backend:
1. Visit your Render URL: `https://your-backend.onrender.com`
2. You should see: `{"message": "Darukaa.Earth API is running", "status": "healthy"}`

### Test Frontend-Backend Connection:
1. Visit your Vercel URL: `https://darukka-earth-bj6a.vercel.app`
2. Try to register a new user
3. Try to login with the registered credentials
4. Check browser console for any errors

## 🔧 Local Development

### Backend:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python main.py
```

Backend will run at: `http://localhost:8000`

### Frontend:
```bash
cd frontend
npm install
npm run dev
```

Frontend will run at: `http://localhost:5173`

## 📝 Environment Variables Summary

### Vercel (Frontend):
- `VITE_API_BASE_URL`: Your Render backend URL (e.g., `https://darukaa-earth-api.onrender.com`)

### Render (Backend):
- No additional environment variables needed for basic setup
- PORT is automatically set by Render

## 🔒 Security Notes

⚠️ **Important for Production:**

1. **Password Hashing:** The current implementation stores passwords in plain text. Before going to production with real users, implement password hashing using `bcrypt` or `passlib`.

2. **Database:** The current implementation uses in-memory storage. Implement a proper database (PostgreSQL, MongoDB, etc.) for production.

3. **JWT Tokens:** Implement proper JWT authentication instead of simple session management.

4. **CORS:** Consider restricting CORS to only your specific domains instead of using `*`.

## 🐛 Troubleshooting

### Login fails with "Network Error":
- Check that `VITE_API_BASE_URL` is set correctly in Vercel
- Verify your Render backend is running (visit the health endpoint)
- Check browser console for CORS errors

### CORS Error:
- Ensure your frontend URL is in the `allow_origins` list in `backend/main.py`
- Redeploy the backend after making CORS changes

### 404 Not Found:
- Verify API endpoints are correctly defined (should be `/api/login` and `/api/register`)
- Check that the backend is deployed and running

## 📞 Need Help?

If issues persist:
1. Check browser console (F12) for detailed error messages
2. Check Render logs for backend errors
3. Check Vercel deployment logs for build issues
