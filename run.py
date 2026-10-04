"""
Root entry point script for Classroom Management project.
Run with: python run.py
"""
import uvicorn
from classroom_management.main import app

if __name__ == "__main__":
    print(" Starting Classroom Management System Server on http://127.0.0.1:8000 ...")
    uvicorn.run("classroom_management.main:app", host="127.0.0.1", port=8000, reload=True)
