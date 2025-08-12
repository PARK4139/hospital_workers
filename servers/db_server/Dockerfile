FROM postgres:15-alpine

# 환경 변수 설정
ENV POSTGRES_DB=hospital_workers
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=password

# 초기화 스크립트 복사
COPY migrations/ /docker-entrypoint-initdb.d/

# 포트 노출
EXPOSE 5432

# PostgreSQL 실행
CMD ["postgres"]
