# 🏥 병원 근무자 관리 시스템

## 📋 프로젝트 개요

병원 근무자 관리 시스템은 Next.js, FastAPI, PostgreSQL, Redis, Nginx를 활용한 현대적인 웹 애플리케이션입니다.

## 🏗️ 아키텍처

### 서비스 구성
- **Page Server**: Next.js + TypeScript + Tailwind CSS + Zustand + NextAuth.js
- **API Server**: FastAPI (Python)
- **Database Server**: PostgreSQL
- **Cache Server**: Redis
- **Reverse Proxy**: Nginx

### 기술 스택
- **Frontend**: Next.js 15, TypeScript, Tailwind CSS, Zustand, NextAuth.js
- **Backend**: FastAPI, Python
- **Database**: PostgreSQL
- **Cache**: Redis
- **Proxy**: Nginx
- **Container**: Docker & Docker Compose

## 🚀 빠른 시작

### 1. 서비스 운영

#### 대화형 메뉴 사용
```bash
python3 scripts/ensure_services_operated.py
```

#### 개별 서비스 실행
```bash
# 전체 서비스 실행 (권장)
python3 scripts/ensure_services_operated.py --all

# 개별 서비스 실행
python3 scripts/ensure_services_operated.py --page-server
python3 scripts/ensure_services_operated.py --api-server
python3 scripts/ensure_services_operated.py --db-server
python3 scripts/ensure_services_operated.py --nginx
python3 scripts/ensure_services_operated.py --redis

# 서비스 상태 확인
python3 scripts/ensure_services_operated.py --status

# 서비스 로그 확인
python3 scripts/ensure_services_operated.py --logs

# 모든 서비스 중지
python3 scripts/ensure_services_operated.py --stop
```

#### 🐳 Docker Compose 직접 사용
```bash
# 서비스 빌드 및 실행
docker compose -f servers/docker-compose.dev.yml up -d

# 서비스 상태 확인
docker compose -f servers/docker-compose.dev.yml ps

# 서비스 로그 확인
docker compose -f servers/docker-compose.dev.yml logs -f

# 서비스 중지
docker compose -f servers/docker-compose.dev.yml down
```

### 2. 서비스 모니터링

#### 대화형 메뉴 사용 (권장)
```bash
./monitors/ensure_service_monitored.sh
```

#### 모니터링 옵션
1. **Page Server 모니터링** - Next.js 서버 상태 및 리소스 사용량
2. **API Server 모니터링** - FastAPI 서버 상태 및 엔드포인트 테스트
3. **Database Server 모니터링** - PostgreSQL 연결 및 성능
4. **Nginx 모니터링** - 리버스 프록시 상태
5. **Redis 모니터링** - 캐시 서버 연결 상태
6. **전체 서비스 모니터링** - 모든 서비스 통합 상태
7. **연속 모니터링** - 실시간 모니터링 (5초 간격)
8. **요약 모니터링** - 서비스 상태 및 리소스 요약

#### 명령행 옵션 사용
```bash
# 연속 모니터링 (실시간)
./monitors/ensure_service_monitored.sh --continuous

# 요약 모니터링
./monitors/ensure_service_monitored.sh --summary

# 상세 모니터링
./monitors/ensure_service_monitored.sh --detailed
```

### 3. 서비스 테스트

#### 자동 테스트 (서비스 실행 시 자동 실행)
```bash
# --all 또는 개별 서비스 실행 시 자동으로 테스트 실행
python3 scripts/ensure_services_operated.py --all
```

#### 테스트 항목
- 📁 파일 구조 테스트 (Docker Compose, Dockerfile, 설정 파일)
- 🔍 Docker Compose 문법 테스트
- 🔍 컨테이너 상태 테스트 (실행 중인 서비스 확인)
- 🔍 포트 연결 테스트 (HTTP, 데이터베이스, Redis)
- 🔍 서비스 간 네트워크 연결 테스트

#### 🧪 Selenium 테스트
```bash
# 로그인 루틴 테스트 (Windows/WSL2)
python -m pytest tests/test_login_routine_via_selenium_at_windows.py -v -s

# 테스트 전제 조건
# - 모든 서비스가 실행 중이어야 함
# - Chrome WebDriver가 설치되어 있어야 함
# - WSL2 환경에서 실행 권장
```

## 📊 서비스 운영 메뉴

### 서비스 선택 옵션
1. **Page Server (Next.js)** - 프론트엔드 서버
2. **API Server (FastAPI)** - 백엔드 API 서버
3. **Database Server (PostgreSQL)** - 데이터베이스 서버
4. **Nginx (Reverse Proxy)** - 리버스 프록시
5. **Redis (Cache)** - 캐시 서버
6. **전체 서비스** - 모든 서비스 실행

### 기능
- ✅ 개별 서비스 선택 실행
- ✅ 서비스별 상태 확인
- ✅ 연결 테스트 자동화
- ✅ 컨테이너 빌드 및 실행
- ✅ 오류 처리 및 로깅

## 🔍 서비스 모니터링 메뉴

### 모니터링 옵션
1. **Page Server 모니터링** - 프론트엔드 서버 상태
2. **API Server 모니터링** - 백엔드 API 서버 상태
3. **Database Server 모니터링** - 데이터베이스 서버 상태
4. **Nginx 모니터링** - 리버스 프록시 상태
5. **Redis 모니터링** - 캐시 서버 상태
6. **전체 서비스 모니터링** - 모든 서비스 종합 모니터링
7. **연속 모니터링 (실시간)** - 실시간 모니터링
8. **요약 모니터링** - 간단한 상태 요약

### 모니터링 항목
- 🐳 Docker 서비스 상태
- 📦 컨테이너 상태 및 리소스 사용량
- 🔌 포트 연결 상태
- 🌐 HTTP 연결 테스트
- 🗄️ 데이터베이스 연결 상태
- 🔴 Redis 연결 상태
- 💾 전체 리소스 사용량
- 🌐 서비스 간 네트워크 연결
- 🧪 API 엔드포인트 테스트

## 📁 프로젝트 구조

```
business_with_ai/
├── services/
│   └── hospital_workers/
│       ├── scripts/                      # 서비스 운영 스크립트
│       │   ├── ensure_services_operated.py      # 통합 서비스 운영 스크립트 (Python)
│       │   └── run_unit_tests.py                # 단위 테스트 실행 스크립트
│       ├── tests/                              # 단위 테스트
│       │   └── test_ensure_services_operated.py # ServiceManager 클래스 테스트
│       ├── monitors/
│       │   └── ensure_service_monitored.sh     # 서비스 모니터링 스크립트
│       ├── servers/                            # 서비스 소스 코드
│       │   ├── page_server/                    # Next.js 프론트엔드
│       │   ├── api_server/                     # FastAPI 백엔드
│       │   ├── db_server/                      # PostgreSQL 데이터베이스
│       │   ├── nginx/                          # Nginx 설정
│       │   ├── docker-compose.dev.yml          # 개발용 Docker Compose
│       │   └── docker-compose.prod.yml         # 운영용 Docker Compose
│       ├── docs/                               # 문서
│       └── logs/                               # 로그
```

## 🛠️ 개발 환경 설정

### 필수 요구사항
- Docker & Docker Compose
- Node.js 18+
- Python 3.8+
- WSL2 (Windows 사용자 권장)

### 환경 설정
```bash
# 1. 프로젝트 클론
git clone <repository-url>
cd business_with_ai/services/hospital_workers

# 2. WSL2 환경에서 실행 (Windows 사용자)
wsl

# 3. 가상환경 활성화
source .venv_linux/bin/activate

# 4. 서비스 실행
python3 scripts/ensure_services_operated.py --all

# 5. 서비스 상태 확인
python3 scripts/ensure_services_operated.py --status

# 6. 단위 테스트 실행
python3 scripts/run_unit_tests.py --all

# 7. 모니터링
./monitors/ensure_service_monitored.sh
```

## 📈 서비스 상태 확인

### 포트 정보 (개발 환경)
- **Page Server**: http://localhost:5173
- **API Server**: http://localhost:8002
- **Nginx**: http://localhost:80
- **Database**: localhost:15432 (외부 접근용)
- **Redis**: localhost:16379 (외부 접근용)

### 내부 포트 (컨테이너 간 통신)
- **Database**: 5432
- **Redis**: 6379
- **API Server**: 8000

### API 엔드포인트
- **Health Check**: `GET /health`
- **Location Guide**: `GET /heal_base_hospital_worker/v1/web/ensure/logined/and/hospital-location-guided/{room}`

## 🔧 문제 해결

### 일반적인 문제
1. **Docker 서비스가 실행되지 않음**
   ```bash
   sudo systemctl start docker
   ```

2. **포트 충돌**
   ```bash
   # 사용 중인 포트 확인
   netstat -tuln | grep :80
   ```

3. **컨테이너 실행 실패**
   ```bash
   # 로그 확인
   docker compose -f servers/docker-compose.dev.yml logs
   ```

4. **한글 깨짐 문제 (Windows/WSL)**
   ```bash
   # 스크립트 파일의 줄바꿈 문자를 LF로 변환
   dos2unix scripts/*.sh
   ```

5. **권한 문제**
   ```bash
   # 스크립트 실행 권한 부여
   chmod +x scripts/*.sh
   ```

### 로그 확인
```bash
# 특정 서비스 로그
docker compose -f servers/docker-compose.dev.yml logs page-server

# 전체 로그
docker compose -f servers/docker-compose.dev.yml logs
```

## 📝 최근 업데이트 (2024-12-19)

### ✅ 해결된 문제들
1. **한글 인코딩 문제**: 모든 스크립트의 한글 주석과 메시지 수정
2. **줄바꿈 문자 문제**: Windows CRLF → Linux LF 변환으로 `bad interpreter` 오류 해결
3. **Docker Compose 경로 문제**: 스크립트 내 경로를 `servers/docker-compose.dev.yml`로 수정
4. **포트 충돌 방지**: 개발 환경에서 DB(15432), Redis(16379) 포트 분리
5. **서비스 상태 파싱 문제**: JSON 상태값(`running`) 인식 및 매핑 로직 개선

### 🔄 개선된 구조
1. **Docker Compose 최적화**: 개발용/운영용 분리
2. **스크립트 통합**: 모든 shell 스크립트를 `ensure_services_operated.py`로 통합
3. **Python 기반**: 크로스 플랫폼 호환성 향상 및 유지보수성 개선
4. **자동 테스트**: 서비스 실행 시 자동으로 환경 및 상태 테스트 실행
5. **단위 테스트**: `ServiceManager` 클래스에 대한 포괄적인 테스트 추가

### 🚀 현재 상태
- ✅ 모든 서비스 정상 실행
- ✅ 컨테이너 간 네트워크 연결 정상
- ✅ 포트 연결 및 HTTP 응답 정상
- ✅ 데이터베이스 및 Redis 연결 정상
- ✅ Python 기반 통합 스크립트 정상 작동
- ✅ 자동 테스트 및 상태 확인 기능 완벽 동작
- ✅ VS Code 태스크 설정 완료 (.vscode/tasks.json)
- ✅ Git 줄바꿈 문자 설정 완료 (.gitattributes)

## 📚 추가 문서

- [API 문서](./docs/api.md)
- [배포 가이드](./docs/deployment.md)
- [개발 가이드](./docs/development.md)
- [아키텍처 문서](./docs/20.ARCHITECTURE.md)
- [비즈니스 제안서](./docs/15.BUSINESS_PROPOSAL.md)

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

**🏥 병원 근무자 관리 시스템** - 현대적이고 효율적인 병원 근무 관리 솔루션



