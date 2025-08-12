FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# pyproject.toml 복사
COPY pyproject.toml ./

# pip로 의존성 직접 설치
RUN pip install --no-cache-dir \
    fastapi>=0.104.0 \
    "uvicorn[standard]>=0.24.0" \
    sqlalchemy>=2.0.0 \
    psycopg2-binary>=2.9.0 \
    redis>=5.0.0 \
    "python-jose[cryptography]>=3.3.0" \
    "passlib[bcrypt]>=1.7.0" \
    python-multipart>=0.0.6 \
    pydantic>=2.0.0 \
    pydantic-settings>=2.0.0

# 소스 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 서비스 실행
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
