from fastapi import APIRouter,Depends, Request,HTTPException,Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, constr
from Src.mysqlDb import get_db
import uuid
from Schema.Schema import userInfo,userLoginInfo
from passlib.context import CryptContext
import time
from jose import jwt
import os
from fastapi.responses import JSONResponse
from Utils.apiResponse import ApiResponse
from Dependencies.verifyJwt import verifyJwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
authRouter = APIRouter()

class Signup(BaseModel):
    fullName: str  # Only letters and spaces, 2–50 chars
    email: EmailStr  # Validates proper email format
    password: str
    

@authRouter.post("/test")
def root():
    return{"hello":"loo"}

@authRouter.post("/signup")
def root(user:Signup,response: Response, db: Session = Depends(get_db)):
    print("came")
    if(db.query(userInfo).filter(userInfo.email == user.email).count() > 0):
      print(db.query(userInfo).filter(userInfo.email == user.email).count())
      raise HTTPException(status_code=401, detail="user already exists")
    userId=str(uuid.uuid4())
    hashedPassword=pwd_context.hash(user.password)
    newUser=userInfo(userId,user.fullName,user.email,hashedPassword,int(time.time()))
    payload={
        "userId":userId,
        "exp": int(time.time()+365*24*3600)
    }
    tokenId=jwt.encode(payload, os.environ.get("JWT_SECRET"), algorithm=os.environ.get("JWT_ALGORITHM"))
    newToken=userLoginInfo(userId,tokenId,int(time.time()))
    # db.add(newUser)
    # db.commit()
    # db.refresh(newUser)
    # db.add(newToken)
    # db.commit()
    # db.refresh(newToken)
    db.add_all([newUser, newToken])
    db.commit()
    #response=JSONResponse(ApiResponse(True, "user created", {"userId": userId,"fullName":user.fullName,"email":user.email}, 200).dict(), status_code=200)

    response.set_cookie(
        key="tokenId",
        value=tokenId,
        max_age=365*24*3600,         # seconds
        expires=365*24*3600,         # seconds
        path="/",
        secure=True,         # True if HTTPS
        httponly=True,        # Prevent JS access
        samesite="strict"        # "strict" | "lax" | "none"
    )
    return{"_id": userId,"fullName":user.fullName,"email":user.email}
#not sending hashed password

class Login(BaseModel):
    email: EmailStr  # Validates proper email format
    password: str
    
@authRouter.post("/login")
def login(user: Login,response: Response, db: Session = Depends(get_db)):
    # 1. Find user by email
    existing_user = db.query(userInfo).filter(userInfo.email == user.email).first()
    if not existing_user:
        raise HTTPException(status_code=402, detail="user does not exists")

    # 2. Verify password
    if not pwd_context.verify(user.password, existing_user.password):
        raise HTTPException(status_code=403, detail="invalid credentials")

    # 3. Create JWT token
    payload = {
        "userId": str(existing_user.userId),
        "exp": int(time.time() + 365 * 24 * 3600)  # 1 year expiry
    }
    tokenId = jwt.encode(
        payload,
        os.environ.get("JWT_SECRET"),
        algorithm=os.environ.get("JWT_ALGORITHM")
    )

    # 4. Save token in DB
    newToken = userLoginInfo(existing_user.userId, tokenId, int(time.time()))
    db.add(newToken)
    db.commit()
    db.refresh(newToken)

    # 5. Send response with HttpOnly cookie
    #response =JSONResponse(ApiResponse(True, "login successful", {"userId": existing_user.userId,"fullName":existing_user.name,"email":user.email}, 200).dict(), status_code=200)

    response.set_cookie(
        key="tokenId",
        value=tokenId,
        max_age=365 * 24 * 3600,
        httponly=True,
        secure=True,       # requires HTTPS
        samesite="strict", # adjust if frontend is on another domain
        path="/"
    )
    return {"_id": existing_user.userId,"fullName":existing_user.name,"email":user.email}
#not sending hashed password
@authRouter.post("/logout")
def logout(request: Request,response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get("tokenId")
    if not token:
        raise HTTPException(status_code=406, detail="invalid token")

    # 1. Delete token entry from DB
    token_entry = db.query(userLoginInfo).filter(userLoginInfo.tokenId == token).first()
    if not token_entry:
        raise HTTPException(status_code=405, detail="invalid token")

    db.delete(token_entry)
    db.commit()

    # 2. Clear cookie
    #response =JSONResponse(ApiResponse(True, "logged out successfully",None,200).dict(), status_code=200)

    response.delete_cookie(key="tokenId", path="/")

    return {"message": "Logout successful"}



@authRouter.get("/check-auth")
async def check_auth(request: Request,userId: str = Depends(verifyJwt),db: Session = Depends(get_db)):
    user = db.query(userInfo).filter(userInfo.userId==userId).first()
    return {
            "_id": str(user.userId),
            "fullName": user.name,
            "email": user.email
        }
#login
#logout
