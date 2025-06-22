from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import smtplib
import os
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from backend.database import SessionLocal, engine, Base
from datetime import datetime, timedelta
from jose import JWTError, jwt

# 환경 변수 로드
load_dotenv()

# 데이터베이스 설정
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    verification_code = Column(String, nullable=True)  # 이메일 인증 코드 저장

Base.metadata.create_all(bind=engine)

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정
SECRET_KEY = os.getenv("SECRET_KEY")  # .env 파일에서 SECRET_KEY 로드
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 액세스 토큰 만료 시간

# JWT 토큰 생성 함수
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# JWT 토큰 검증 함수
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token has expired or is invalid")

# FastAPI 라우터 설정
router = APIRouter()

# 이메일 전송 함수
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# 데이터베이스 연결 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 회원가입 요청 데이터 모델
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# 이메일 인증 요청 데이터 모델
class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str

# 이메일 전송 함수
def send_verification_email(to_email: str, code: str):
    try:
        subject = "이메일 인증 코드"
        body = f"이메일 인증 코드: {code}"
        message = f"Subject: {subject}\n\n{body}"

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, message)
        server.quit()
    except Exception as e:
        print("이메일 전송 실패:", e)

# 랜덤 인증 코드 생성
import random
import string

def generate_verification_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# 회원가입 엔드포인트
@router.post("/register/")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")

    hashed_password = pwd_context.hash(user.password)
    verification_code = generate_verification_code()

    new_user = User(email=user.email, hashed_password=hashed_password, verification_code=verification_code)
    db.add(new_user)
    db.commit()

    send_verification_email(user.email, verification_code)
    return {"message": "회원가입 성공! 이메일로 인증 코드를 발송했습니다."}

# 이메일 인증 엔드포인트
@router.post("/verify-email/")
def verify_email(request: VerifyEmailRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="존재하지 않는 이메일입니다.")

    if user.verification_code != request.code:
        raise HTTPException(status_code=400, detail="잘못된 인증 코드입니다.")

    user.verification_code = None  # 인증 완료 후 코드 삭제
    db.commit()
    return {"message": "이메일 인증이 완료되었습니다!"}

# 로그인 엔드포인트
@router.post("/token/")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 올바르지 않습니다.")
    
    # JWT 토큰 생성
    access_token = create_access_token(data={"sub": db_user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}
