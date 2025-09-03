# models.py
from sqlalchemy import Column, Integer, String,BigInteger,Text
from datetime import datetime
import time
from Src.mysqlDb import Base


class userInfo(Base):
    __tablename__ = "userInfo"

    userId = Column(String(300), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)
    timestamp = Column(BigInteger, default=lambda: int(time.time() * 1000))

    def __init__(self, userId: str, name: str, email: str, password: str, timestamp: datetime = None):
        self.userId = userId
        self.name = name
        self.email = email
        self.password = password
        self.timestamp = timestamp if timestamp else datetime.now()

    def __repr__(self):
        return f"<userInfo(userId={self.userId}, name={self.name}, email={self.email})>"


class resumeInfo(Base):
    __tablename__ = "resumeInfo"

    contentId = Column(String(300), primary_key=True, index=True)
    contentName = Column(String(100), nullable=False)
    userId = Column(String(300), nullable=False, index=True)
    ipAddress = Column(String(255), nullable=False)
    timestamp = Column(BigInteger, default=lambda: int(time.time() * 1000))

    def __init__(self, contentId: str, contentName: str, userId: str, ipAddress: str, timestamp: datetime = None):
        self.contentId = contentId
        self.contentName = contentName
        self.userId = userId
        self.ipAddress = ipAddress
        self.timestamp = timestamp if timestamp else datetime.now()

    def __repr__(self):
        return f"<resumeInfo(contentId={self.contentId}, userId={self.userId}, contentName={self.contentName})>"


class userLoginInfo(Base):
    __tablename__ = "userLoginInfo"

    userId = Column(String(300), nullable=False)
    tokenId = Column(String(255), primary_key=True, index=True, nullable=False)
    timestamp = Column(BigInteger, default=lambda: int(time.time() * 1000))

    def __init__(self, userId: str, tokenId: str, timestamp: datetime = None):
        self.userId = userId
        self.tokenId = tokenId
        self.timestamp = timestamp if timestamp else datetime.now()

    def __repr__(self):
        return f"<userLoginInfo(userId={self.userId}, tokenId={self.tokenId})>"


class resumeHistory(Base):
    __tablename__ = "resumeHistory"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userId = Column(String(300), nullable=False)
    ResumeId = Column(String(300), nullable=False)
    aiFeedback = Column(Text, nullable=False)
    jd = Column(Text,nullable=False)
    score = Column(Integer,nullable=False)
    timestamp = Column(BigInteger, default=lambda: int(time.time() * 1000))

    def __init__(self, userId: str, ResumeId: str, aiFeedback: str, jd: str,score: int, timestamp: datetime = None):
        self.userId = userId
        self.ResumeId = ResumeId
        self.aiFeedback = aiFeedback
        self.jd = jd
        self.score = score
        self.timestamp = timestamp if timestamp else datetime.now()

    def __repr__(self):
        return f"<resumeHistory(id={self.id}, userId={self.userId}, ResumeId={self.ResumeId})>"