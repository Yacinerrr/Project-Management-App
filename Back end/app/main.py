from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Project Management API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Project Management API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}