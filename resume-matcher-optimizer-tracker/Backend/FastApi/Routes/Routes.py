from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Controllers.test import testRouter
from Controllers.auth import authRouter
from Controllers.ResumeJd import ResumeJdRouter
from Controllers.hrDashboard import HrRouter
masterRouter = APIRouter()

masterRouter.include_router(testRouter, prefix="/test")
masterRouter.include_router(authRouter, prefix="/auth")
masterRouter.include_router(ResumeJdRouter, prefix="/resume")
masterRouter.include_router(HrRouter, prefix="/hr")
