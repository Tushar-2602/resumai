from fastapi import APIRouter, Form, File, UploadFile, HTTPException, Depends,Request
from sqlalchemy.orm import Session
from PyPDF2 import PdfReader
import uuid, time
from Src.mysqlDb import get_db
from Schema.Schema import resumeInfo,resumeHistory  # Your SQLAlchemy model
from Utils.apiResponse import ApiResponse
from fastapi.responses import JSONResponse
from Dependencies.verifyJwt import verifyJwt
from GenAi.GeminiApis import getMatchedResponse
import boto3
from GenAi.Pinecone import saveToPine
import os
from typing import Optional

ResumeJdRouter = APIRouter()

# S3 config (replace with your credentials or use environment/role-based auth)
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
    
@ResumeJdRouter.post("/saveResumeOrScore")
async def save_resume_or_score(
    contentName: Optional[str] = Form(None),   # Candidate name
    jd_text: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    userId: str = Depends(verifyJwt),
    request: Request = None
):
    contentName="hello"
    # 1️⃣ Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="file must be a PDF")

    # 2️⃣ Check file size (<5 MB)
    file.file.seek(0, 2)         # move to end
    file_size = file.file.tell() # current pointer = size in bytes
    file.file.seek(0)  
    
    if file_size > 5 * 1024 * 1024:  # 5 MB
        raise HTTPException(status_code=400, detail="Resume file too large")
  
    
    if len(jd_text)>100000:
            raise HTTPException(status_code=500, detail=f"jd too long")
    # 3️⃣ Read PDF
    try:
        pdf_reader = PdfReader(file.file)
        num_pages = len(pdf_reader.pages)
        if num_pages < 1 or num_pages > 3:
            raise HTTPException(status_code=400, detail="Resume must have 1 to 3 pages")
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        if len(text.strip()) < 100:
            raise HTTPException(status_code=400, detail="Resume text too short")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

    # 4️⃣ Check if candidate name already exists for this user
    existing = db.query(resumeInfo).filter(
        resumeInfo.contentName == contentName,
        resumeInfo.userId == userId
    ).first()

    # if existing:
    #     raise HTTPException(status_code=400, detail="resume name already exists for this user")

    # 5️⃣ Upload to S3
    while True:
        contentId = str(uuid.uuid4())
        # Check if contentId already exists
        existing = db.query(resumeInfo).filter(resumeInfo.contentId == contentId).first()
        if not existing:
          break
    try:
        s3_key = f"resumes/{contentId}.pdf"
        file.file.seek(0)
        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET,
            s3_key,
            ExtraArgs={"ContentType": "application/pdf"}
        )
        #s3_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading to S3: {str(e)}")
    # save in pinecone
    vectorResp=saveToPine(text,contentId)
    if not vectorResp:
        raise HTTPException(status_code=500, detail=f"vector db error")
    # 6️⃣ Save record in DB
    ip = request.headers.get("X-Forwarded-For", request.client.host)
    new_resume = resumeInfo(
        contentId=contentId,
        contentName=contentName,
        userId=userId,
        ipAddress=ip,
        timestamp=int(time.time() * 1000)
    )
    db.add(new_resume)
    db.commit()

    # 7️⃣ Optional AI scoring
    if len(jd_text.strip())>10:
        aiResponse = getMatchedResponse(text, jd_text)
        print(aiResponse)
        dbstore=" ~ ".join(aiResponse["aiFeedback"])
        newResumeResp = resumeHistory(
            userId, contentId, str(dbstore), jd_text, aiResponse["score"], int(time.time())
        )
        db.add(newResumeResp)
        db.commit()
        return {"driveUrl": "",
            "aiFeedback":aiResponse["aiFeedback"],
            "score": aiResponse["score"]
            }

    return  {"driveUrl": "",
            "aiFeedback":["aiFeedback"],
            "score": 8
            }


@ResumeJdRouter.post("/history")
async def get_resume_history(
    userId: str = Depends(verifyJwt),
    db: Session = Depends(get_db)
):
    try:
        # Fetch all resumes for this user
        histories = db.query(resumeHistory).filter(resumeHistory.userId == userId).all()
        
        response_data = []
        for h in histories:
            arr = h.aiFeedback.split("~")
            signed_url = generate_signed_url(h.ResumeId)
            response_data.append({
                "driveUrl": signed_url,
                "aiFeedback": arr,
                "score": h.score,
                "uploadedAt": h.timestamp
            })
        
        return {"resumes":response_data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))