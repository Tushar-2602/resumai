from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
import  os, time
from jose import jwt
from Utils.apiResponse import ApiResponse
from Src.mysqlDb import get_db
from Schema.Schema import userLoginInfo, userInfo

def verifyJwt(request: Request, db: Session = Depends(get_db)):
    # 1. Extract token from cookies
    token = request.cookies.get("tokenId")
    if not token:
        raise HTTPException(status_code=400, detail="invalid token")

    try:
        # 2. Decode token
        payload = jwt.decode(
            token,
            os.environ.get("JWT_SECRET"),
            algorithms=[os.environ.get("JWT_ALGORITHM")]
        )
        user_id = payload.get("userId")

        if not user_id:
            raise HTTPException(status_code=401, detail="invalid token")
        # 3. Check if token exists in DB
        token_entry = db.query(userLoginInfo).filter(userLoginInfo.tokenId == token).first()
        if not token_entry:
            raise HTTPException(status_code=402, detail="invalid token")

        # 4. (Optional) Check if user still exists
        user = db.query(userInfo).filter(userInfo.userId == user_id).first()
        if not user:
            raise HTTPException(status_code=403, detail="invalid token")

        # ✅ Token verified — return user (or payload)
        return user.userId

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=404, detail="invalid token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=405, detail="invalid token")

