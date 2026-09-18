"""
Vercel Serverless Function Handler for FastAPI
"""
from main import app

# Vercel requires a handler variable
handler = app
