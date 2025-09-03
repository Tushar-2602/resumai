from fastapi import APIRouter
from sqlalchemy.orm import Session

testRouter = APIRouter()

@testRouter.get("")
def root():
    return {"message": "FastAPI is running"}