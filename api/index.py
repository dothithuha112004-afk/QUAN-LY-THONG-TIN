import sys
import os

# Add root directory to python path for Vercel serverless execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classroom_management.main import app

# Vercel ASGI Application Handler
app = app
