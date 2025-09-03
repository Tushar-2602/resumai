from fastapi import APIRouter, Form, File, UploadFile, HTTPException, Depends,Request
from sqlalchemy.orm import Session
from PyPDF2 import PdfReader
import uuid, time
from pydantic import BaseModel
from Src.mysqlDb import get_db
from Schema.Schema import resumeInfo,resumeHistory,userInfo  # Your SQLAlchemy model
from Utils.apiResponse import ApiResponse
from fastapi.responses import JSONResponse
from Dependencies.verifyJwt import verifyJwt
from GenAi.GeminiApis import getMatchedResponse
import boto3
from GenAi.Pinecone import saveToPine,getFromPine
import os

HrRouter = APIRouter()

class JobDesc(BaseModel):
    jd: str

# Initialize S3 client
S3_BUCKET = os.environ.get("S3_name", "myuser")
S3_REGION = os.environ.get("S3_region", "myuser")
AWS_ACCESS_KEY_ID = os.environ.get("S3_access_key", "myuser")
AWS_SECRET_ACCESS_KEY = os.environ.get("S3_secret_key", "myuser")
s3_client = boto3.client(
    "s3",
    region_name=S3_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def generate_signed_url(contentId: str, expires_in: int = 10000):
    key = f"resumes/{contentId}.pdf"
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": key},
        ExpiresIn=expires_in
    )

@HrRouter.post("/getResumes")
async def get_resumes(
    jd_text: str=Form(...),
    db: Session = Depends(get_db)
):
    jd = jd_text.strip()
    if len(jd) < 10 or len(jd) > 100000:
        raise HTTPException(
            status_code=400,
            detail="Job description must be between 100 and 100000 characters."
        )

    # 1. Query Pinecone
    results = getFromPine(jd)  # adjust top_k as needed
    if not results["matches"]:
        raise HTTPException(status_code=404, detail="No matching content found.")

    content_ids = [m["id"] for m in results["matches"]]
    scores = [m["score"] for m in results["matches"]]

    # 2. Fetch user_name by joining resumeInfo and userInfo
    query = (
        db.query(resumeInfo.contentId, resumeInfo.userId, userInfo.name)
        .join(userInfo, resumeInfo.userId == userInfo.userId)
        .filter(resumeInfo.contentId.in_(content_ids))
    )
    content_user_map = {row.contentId: row.name for row in query.all()}

    # 3. Build final array
    response_array = []
    for content_id, score in zip(content_ids, scores):
        signed_url = generate_signed_url(content_id)
        user_name = content_user_map.get(content_id, "Unknown")
        response_array.append({
            "score": round(score*100,4),
            "driveUrl": signed_url,
            "name": user_name
        })
    return {"topResumes":response_array}
