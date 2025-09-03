from fastapi import FastAPI, Depends,APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import text
from .mysqlDb import Base, engine  # Import your get_db function
from Routes.Routes import masterRouter
from fastapi.middleware.cors import CORSMiddleware



# Create FastAPI instance
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic GET route
app.include_router(masterRouter, prefix="/api/v1")

Base.metadata.create_all(bind=engine)
