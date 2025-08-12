# Hospital Workers Service

## 🏗️ MSA 아키텍처 구조

### 서비스 구성
- **로그인 서버** (`auth-service`): 사용자 인증 전담
- **API 서버** (`api-service`): 비즈니스 로직 처리
- **User DB** (`user-db`): 사용자 데이터베이스

### 기술 스택
- **API**: FastAPI
- **가상환경**: 
  - 서비스: Docker Compose
  - 파이썬: uv.lock, pyproject.toml
  - 도커: Dockerfile.dev/Dockerfile.prod (개발/프로덕션 분리)
- **아키텍처**: DDD + MSA

## 🐳 Docker 구성

### 개발 환경 (Dockerfile.dev)
- 볼륨 마운트로 코드 변경사항 즉시 반영
- 빠른 개발 속도

### 프로덕션 환경 (Dockerfile.prod)
- 멀티스테이지 빌드로 이미지 크기 최소화
- 최적화된 성능

### 서비스별 컨테이너
```yaml
# docker-compose.yml
services:
  auth-service:    # 로그인 서버
  api-service:     # API 서버
  user-db:         # 사용자 데이터베이스
  nginx:           # 리버스 프록시
  redis:           # 캐시/세션
```

## 🔗 API/Web 엔드포인트 설계

### API 엔드포인트
- `POST /heal_base_hospital_worker/v1/api/ensure/login/` - 로그인 API

### Web 엔드포인트
- `GET /heal_base_hospital_worker/v1/web/ensure/login/` - 로그인 (메인화면)
- `GET /heal_base_hospital_worker/v1/web/ensure/login-guide/` - 로그인 (가이드)
- `GET /heal_base_hospital_worker/v1/web/ensure/login-google-id` - 로그인 (구글)
- `GET /heal_base_hospital_worker/v1/web/ensure/signup/` - 회원가입
- `POST /heal_base_hospital_worker/v1/web/ensure/signup-form-submit/` - 회원가입 폼 제출
- `GET /heal_base_hospital_worker/v1/web/ensure/signup-complete/` - 회원가입 완료
- `GET /heal_base_hospital_worker/v1/web/ensure/logined/and/hospital-location-guided/{실}` - 실별위치가이드 + 광고

## 📂 프로젝트 구조
```
services/hospital_workers/
├── auth-service/          # 로그인 서버
│   ├── Dockerfile.dev    # 개발용 도커파일
│   ├── Dockerfile.prod   # 프로덕션용 도커파일
│   └── pyproject.toml
├── api-service/           # API 서버
│   ├── Dockerfile.dev
│   ├── Dockerfile.prod
│   └── pyproject.toml
├── user-db/              # 사용자 데이터베이스
├── shared/               # 공통 모듈
├── docker-compose.dev.yml # 개발용 Docker Compose
├── docker-compose.prod.yml # 프로덕션용 Docker Compose
└── README.md            # 이 파일
```

## 🚀 개발 환경 설정

### 개발 모드 실행
```bash
# 개발 환경 (볼륨 마운트, 즉시 반영)
docker-compose -f docker-compose.dev.yml up -d
```

### 프로덕션 모드 실행
```bash
# 프로덕션 환경 (최적화된 빌드)
docker-compose -f docker-compose.prod.yml up -d
```
