from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import uvicorn
import hashlib
import secrets
from datetime import datetime, timedelta

# 데이터베이스 및 모델 import
from .database import get_db, init_db
from .models import User, Department, UserSession

# Pydantic 모델들
class UserLogin(BaseModel):
    email: str
    password: str

class UserSignup(BaseModel):
    first_name: str
    last_name: str
    email: str
    department: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    department: str
    is_active: bool
    is_verified: bool

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# 보안 설정
security = HTTPBearer()

app = FastAPI(
    title="Hospital Workers Auth Service",
    description="인증 서비스 - 로그인 및 회원가입",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """앱 시작 시 데이터베이스 초기화"""
    init_db()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hospital Workers Auth Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "auth-service"}

# 유틸리티 함수들
def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return hash_password(plain_password) == hashed_password

def create_session_token() -> str:
    """세션 토큰 생성"""
    return secrets.token_urlsafe(32)

# API 엔드포인트
@app.post("/auth/login", response_model=LoginResponse)
async def login_api(user_data: UserLogin, db: Session = Depends(get_db)):
    """사용자 로그인"""
    # 사용자 찾기
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )
    
    # 비밀번호 검증
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )
    
    # 계정 상태 확인
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비활성화된 계정입니다."
        )
    
    # 세션 토큰 생성
    session_token = create_session_token()
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    # 기존 세션 삭제 (하나의 계정당 하나의 세션만 허용)
    db.query(UserSession).filter(UserSession.user_id == user.id).delete()
    
    # 새 세션 생성
    new_session = UserSession(
        user_id=user.id,
        session_token=session_token,
        expires_at=expires_at
    )
    db.add(new_session)
    
    # 마지막 로그인 시간 업데이트
    user.last_login = datetime.utcnow()
    
    db.commit()
    
    # 부서 정보 가져오기
    department_name = "알 수 없음"
    if user.department_id:
        dept = db.query(Department).filter(Department.id == user.department_id).first()
        if dept:
            department_name = dept.name
    
    return LoginResponse(
        access_token=session_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            department=department_name,
            is_active=user.is_active,
            is_verified=user.is_verified
        )
    )

# Web 엔드포인트
@app.get("/heal_base_hospital_worker/v1/web/ensure/login/")
async def login_main():
    return {"message": "로그인 메인화면", "status": "success"}

@app.get("/heal_base_hospital_worker/v1/web/ensure/login-guide/")
async def login_guide():
    return {"message": "로그인 가이드", "status": "success"}

@app.get("/heal_base_hospital_worker/v1/web/ensure/login-via-google")
async def login_google():
    return {"message": "구글 로그인", "status": "success"}

@app.get("/heal_base_hospital_worker/v1/web/ensure/signup/")
async def signup_page():
    return {"message": "회원가입 페이지", "status": "success"}

@app.post("/auth/signup", response_model=UserResponse)
async def signup_api(user_data: UserSignup, db: Session = Depends(get_db)):
    """사용자 회원가입"""
    # 이메일 중복 확인
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다."
        )
    
    # 부서 ID 찾기
    department = db.query(Department).filter(Department.name == user_data.department).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 부서입니다."
        )
    
    # 비밀번호 해싱
    hashed_password = hash_password(user_data.password)
    
    # 새 사용자 생성
    new_user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        hashed_password=hashed_password,
        department_id=department.id,
        is_active=True,
        is_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        department=department.name,
        is_active=new_user.is_active,
        is_verified=new_user.is_verified
    )

@app.post("/auth/create-test-account")
async def create_test_account(db: Session = Depends(get_db)):
    """테스트 계정 생성 (foo@foo / foo)"""
    # 이미 존재하는지 확인
    existing_user = db.query(User).filter(User.email == "foo@foo").first()
    if existing_user:
        return {"message": "테스트 계정이 이미 존재합니다.", "email": "foo@foo", "password": "foo"}
    
    # 응급실 부서 찾기
    department = db.query(Department).filter(Department.name == "응급실").first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="응급실 부서를 찾을 수 없습니다."
        )
    
    # 테스트 계정 생성
    hashed_password = hash_password("foo")
    test_user = User(
        email="foo@foo",
        first_name="테스트",
        last_name="사용자",
        hashed_password=hashed_password,
        department_id=department.id,
        is_active=True,
        is_verified=True
    )
    
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    return {
        "message": "테스트 계정이 생성되었습니다.",
        "email": "foo@foo",
        "password": "foo",
        "user_id": test_user.id
    }

@app.get("/heal_base_hospital_worker/v1/web/ensure/signup-complete/")
async def signup_complete():
    return {"message": "회원가입 완료", "status": "success"}

@app.get("/heal_base_hospital_worker/v1/web/ensure/logined/and/hospital-location-guided/{room}")
async def location_guide(room: str):
    return {
        "message": f"{room}실 위치 가이드",
        "room": room,
        "status": "success",
        "advertisement": "광고 정보"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
