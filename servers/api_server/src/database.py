from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from .models import Base

# 데이터베이스 URL 환경변수에서 가져오기
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db-server:5432/hospital_workers")

# 엔진 생성
engine = create_engine(DATABASE_URL)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """데이터베이스 세션을 반환하는 의존성 함수"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """데이터베이스 테이블 생성"""
    Base.metadata.create_all(bind=engine)

def init_db():
    """데이터베이스 초기화 및 기본 데이터 삽입"""
    from .models import Department, Room, LocationGuide
    
    create_tables()
    
    db = SessionLocal()
    try:
        # 기본 부서 데이터 확인 및 삽입
        departments = [
            {"name": "응급실", "description": "응급 환자 치료", "floor": 1},
            {"name": "내과", "description": "내과 질환 치료", "floor": 2},
            {"name": "외과", "description": "외과 수술 및 치료", "floor": 2},
            {"name": "소아과", "description": "소아 질환 치료", "floor": 3},
            {"name": "산부인과", "description": "산부인과 진료", "floor": 3},
            {"name": "영상의학과", "description": "의료 영상 진단", "floor": 1},
            {"name": "검사실", "description": "의료 검사 및 분석", "floor": 1},
            {"name": "간호부", "description": "간호 서비스", "floor": 1},
        ]
        
        for dept_data in departments:
            existing = db.query(Department).filter(Department.name == dept_data["name"]).first()
            if not existing:
                dept = Department(**dept_data)
                db.add(dept)
        
        db.commit()
        
        # 기본 병실 데이터 확인 및 삽입
        rooms = [
            {"room_number": "101", "floor": 1, "department_id": 1, "capacity": 2},
            {"room_number": "102", "floor": 1, "department_id": 1, "capacity": 2},
            {"room_number": "103", "floor": 1, "department_id": 1, "capacity": 2},
            {"room_number": "201", "floor": 2, "department_id": 2, "capacity": 1},
            {"room_number": "202", "floor": 2, "department_id": 2, "capacity": 1},
            {"room_number": "203", "floor": 2, "department_id": 3, "capacity": 1},
            {"room_number": "301", "floor": 3, "department_id": 4, "capacity": 1},
            {"room_number": "302", "floor": 3, "department_id": 4, "capacity": 1},
            {"room_number": "303", "floor": 3, "department_id": 5, "capacity": 1},
        ]
        
        for room_data in rooms:
            existing = db.query(Room).filter(Room.room_number == room_data["room_number"]).first()
            if not existing:
                room = Room(**room_data)
                db.add(room)
        
        db.commit()
        
        # 기본 위치 가이드 데이터 확인 및 삽입
        guides = [
            {"room_id": 1, "guide_text": "1층 응급실 101호", "directions": "엘리베이터에서 내려서 왼쪽으로 20m", "landmarks": "응급실 간호사실 옆"},
            {"room_id": 2, "guide_text": "1층 응급실 102호", "directions": "엘리베이터에서 내려서 왼쪽으로 30m", "landmarks": "응급실 치료실 옆"},
            {"room_id": 3, "guide_text": "1층 응급실 103호", "directions": "엘리베이터에서 내려서 왼쪽으로 40m", "landmarks": "응급실 대기실 옆"},
            {"room_id": 4, "guide_text": "2층 내과 201호", "directions": "2층 엘리베이터에서 오른쪽으로 15m", "landmarks": "내과 진료실 옆"},
            {"room_id": 5, "guide_text": "2층 내과 202호", "directions": "2층 엘리베이터에서 오른쪽으로 25m", "landmarks": "내과 검사실 옆"},
            {"room_id": 6, "guide_text": "2층 외과 203호", "directions": "2층 엘리베이터에서 왼쪽으로 20m", "landmarks": "외과 수술실 옆"},
            {"room_id": 7, "guide_text": "3층 소아과 301호", "directions": "3층 엘리베이터에서 오른쪽으로 10m", "landmarks": "소아과 진료실 옆"},
            {"room_id": 8, "guide_text": "3층 소아과 302호", "directions": "3층 엘리베이터에서 오른쪽으로 20m", "landmarks": "소아과 검사실 옆"},
            {"room_id": 9, "guide_text": "3층 산부인과 303호", "directions": "3층 엘리베이터에서 왼쪽으로 15m", "landmarks": "산부인과 진료실 옆"},
        ]
        
        for guide_data in guides:
            existing = db.query(LocationGuide).filter(LocationGuide.room_id == guide_data["room_id"]).first()
            if not existing:
                guide = LocationGuide(**guide_data)
                db.add(guide)
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
