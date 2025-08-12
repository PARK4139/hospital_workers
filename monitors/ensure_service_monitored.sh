#!/bin/bash

# 서비스 모니터링 스크립트 (개선된 버전)
# 사용법: ./monitors/ensure_service_monitored.sh [옵션]
# 옵션: --continuous, --summary, --detailed

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 서비스 정의
declare -A SERVICES=(
    [1]="page-server"
    [2]="api-server"
    [3]="db-server"
    [4]="nginx"
    [5]="redis"
    [6]="all"
)

# 메뉴 표시 함수
show_monitoring_menu() {
    echo -e "${CYAN}🔍 병원 근무자 관리 시스템 모니터링${NC}"
    echo "=================================="
    echo -e "${YELLOW}📋 모니터링 옵션:${NC}"
    echo "1. Page Server 모니터링"
    echo "2. API Server 모니터링"
    echo "3. Database Server 모니터링"
    echo "4. Nginx 모니터링"
    echo "5. Redis 모니터링"
    echo "6. 전체 서비스 모니터링"
    echo "7. 연속 모니터링 (실시간)"
    echo "8. 요약 모니터링"
    echo "0. 종료"
    echo "=================================="
}

# 서비스별 상세 모니터링 함수
monitor_service() {
    local service=$1
    local service_name=$2
    
    echo -e "${BLUE}🔍 $service_name 모니터링...${NC}"
    echo "----------------------------------------"
    
    # 컨테이너 상태 확인
    if docker compose -f services/hospital_workers/docker-compose.yml ps | grep -q "$service.*Up"; then
        echo -e "${GREEN}✅ $service_name 실행 중${NC}"
        
        # 컨테이너 상세 정보
        container_id=$(docker compose -f services/hospital_workers/docker-compose.yml ps -q $service)
        if [ ! -z "$container_id" ]; then
            echo "🔍 컨테이너 정보:"
            echo "   📦 컨테이너 ID: $container_id"
            echo "   🏷️  컨테이너 이름: $service"
            echo "   📊 컨테이너 상태: $(docker inspect --format='{{.State.Status}}' $container_id)"
            echo "   ⏰ 시작 시간: $(docker inspect --format='{{.State.StartedAt}}' $container_id | cut -d'T' -f1)"
            
            # 리소스 사용량
            echo "   🔍 메모리 사용량:"
            docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}" $container_id
            echo "   🔍 CPU 사용량:"
            docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.PIDs}}" $container_id
        fi
        
        # 서비스별 로그 확인 (최근 3줄)
        echo "📋 최근 로그 (3줄):"
        docker compose -f services/hospital_workers/docker-compose.yml logs --tail=3 $service
        
        # 서비스별 연결 테스트
        case $service in
            "page-server")
                if curl -s -o /dev/null -w "%{http_code}" http://localhost:5173 | grep -q "200\|301\|302"; then
                    echo -e "${GREEN}✅ Page Server HTTP 연결 성공${NC}"
                else
                    echo -e "${RED}❌ Page Server HTTP 연결 실패${NC}"
                fi
                ;;
            "api-server")
                if curl -s -o /dev/null -w "%{http_code}" http://localhost:8002/health | grep -q "200"; then
                    echo -e "${GREEN}✅ API Server HTTP 연결 성공${NC}"
                else
                    echo -e "${RED}❌ API Server HTTP 연결 실패${NC}"
                fi
                ;;
            "nginx")
                if curl -s -o /dev/null -w "%{http_code}" http://localhost:80 | grep -q "200\|301\|302"; then
                    echo -e "${GREEN}✅ Nginx HTTP 연결 성공${NC}"
                else
                    echo -e "${RED}❌ Nginx HTTP 연결 실패${NC}"
                fi
                ;;
            "db-server")
                if docker compose -f services/hospital_workers/docker-compose.yml exec -T db-server pg_isready -U postgres > /dev/null 2>&1; then
                    echo -e "${GREEN}✅ PostgreSQL 연결 성공${NC}"
                else
                    echo -e "${RED}❌ PostgreSQL 연결 실패${NC}"
                fi
                ;;
            "redis")
                if docker compose -f services/hospital_workers/docker-compose.yml exec -T redis redis-cli ping | grep -q "PONG"; then
                    echo -e "${GREEN}✅ Redis 연결 성공${NC}"
                else
                    echo -e "${RED}❌ Redis 연결 실패${NC}"
                fi
                ;;
        esac
        
    else
        echo -e "${RED}❌ $service_name 실행 실패${NC}"
        
        # 실패한 서비스의 로그 확인
        echo "📋 실패 로그:"
        docker compose -f services/hospital_workers/docker-compose.yml logs --tail=5 $service
    fi
    echo "----------------------------------------"
}

# 포트 연결 모니터링 함수
monitor_ports() {
    echo -e "${BLUE}🔌 포트 연결 모니터링...${NC}"
    ports=(
        "80:nginx"
        "5173:page-server"
        "8002:api-server"
        "5432:db-server"
        "6379:redis"
    )

    echo "🔍 각 포트 상태:"
    for port_info in "${ports[@]}"; do
        port=$(echo $port_info | cut -d: -f1)
        service=$(echo $port_info | cut -d: -f2)
        
        if netstat -tuln | grep -q ":$port "; then
            echo -e "${GREEN}✅ 포트 $port ($service) 사용 중${NC}"
        else
            echo -e "${RED}❌ 포트 $port ($service) 연결 실패${NC}"
        fi
    done
    echo "=================================="
}

# HTTP 연결 모니터링 함수
monitor_http_connections() {
    echo -e "${BLUE}🌐 HTTP 연결 모니터링...${NC}"
    sleep 2

    echo "🔍 HTTP 연결 테스트:"
    
    # Page Server 테스트
    echo "📋 Page Server (포트 5173):"
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:5173 | grep -q "200\|301\|302"; then
        echo -e "${GREEN}✅ Page Server HTTP 연결 성공${NC}"
    else
        echo -e "${RED}❌ Page Server HTTP 연결 실패${NC}"
    fi

    # API Server 테스트
    echo "📋 API Server (포트 8002):"
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8002/health | grep -q "200"; then
        echo -e "${GREEN}✅ API Server HTTP 연결 성공${NC}"
    else
        echo -e "${RED}❌ API Server HTTP 연결 실패${NC}"
    fi

    # Nginx 테스트
    echo "📋 Nginx (포트 80):"
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:80 | grep -q "200\|301\|302"; then
        echo -e "${GREEN}✅ Nginx HTTP 연결 성공${NC}"
    else
        echo -e "${RED}❌ Nginx HTTP 연결 실패${NC}"
    fi
    echo "=================================="
}

# 데이터베이스 연결 모니터링 함수
monitor_database() {
    echo -e "${BLUE}🗄️ 데이터베이스 연결 모니터링...${NC}"
    if docker compose -f services/hospital_workers/docker-compose.yml exec -T db-server pg_isready -U postgres > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PostgreSQL 연결 성공${NC}"
    else
        echo -e "${RED}❌ PostgreSQL 연결 실패${NC}"
    fi
    echo "=================================="
}

# Redis 연결 모니터링 함수
monitor_redis() {
    echo -e "${BLUE}🔴 Redis 연결 모니터링...${NC}"
    if docker compose -f services/hospital_workers/docker-compose.yml exec -T redis redis-cli ping | grep -q "PONG"; then
        echo -e "${GREEN}✅ Redis 연결 성공${NC}"
    else
        echo -e "${RED}❌ Redis 연결 실패${NC}"
    fi
    echo "=================================="
}

# 전체 리소스 사용량 모니터링 함수
monitor_resources() {
    echo -e "${BLUE}💾 전체 리소스 사용량 모니터링...${NC}"
    echo "🔍 모든 컨테이너 리소스 사용량:"
    echo "   📊 서비스별 상세 정보:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}"
    echo "=================================="
}

# 네트워크 연결 모니터링 함수
monitor_network() {
    echo -e "${BLUE}🌐 서비스 간 네트워크 연결 모니터링...${NC}"
    if docker compose -f services/hospital_workers/docker-compose.yml exec -T api-server sh -c "timeout 5 bash -c '</dev/tcp/db-server/5432'" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ api-server → db-server 연결 성공${NC}"
    else
        echo -e "${RED}❌ api-server → db-server 연결 실패${NC}"
    fi

    if docker compose -f services/hospital_workers/docker-compose.yml exec -T api-server sh -c "timeout 5 bash -c '</dev/tcp/redis/6379'" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ api-server → redis 연결 성공${NC}"
    else
        echo -e "${RED}❌ api-server → redis 연결 실패${NC}"
    fi
    echo "=================================="
}

# API 엔드포인트 모니터링 함수
monitor_api_endpoints() {
    echo -e "${BLUE}🧪 API 엔드포인트 모니터링...${NC}"
    echo "📋 API Server 엔드포인트 테스트:"
    curl -s http://localhost:8002/ | jq . 2>/dev/null || curl -s http://localhost:8002/

    echo "📋 위치 가이드 API 테스트:"
    curl -s http://localhost:8002/heal_base_hospital_worker/v1/web/ensure/logined/and/hospital-location-guided/101 | jq . 2>/dev/null || curl -s http://localhost:8002/heal_base_hospital_worker/v1/web/ensure/logined/and/hospital-location-guided/101
    echo "=================================="
}

# 연속 모니터링 함수
continuous_monitoring() {
    echo -e "${PURPLE}🔄 연속 모니터링 시작... (Ctrl+C로 종료)${NC}"
    echo "=================================="
    
    while true; do
        clear
        echo -e "${CYAN}🔍 실시간 모니터링 - $(date)${NC}"
        echo "=================================="
        
        # 전체 서비스 상태 요약
        echo -e "${YELLOW}📊 전체 서비스 상태:${NC}"
        docker compose -f services/hospital_workers/docker-compose.yml ps
        
        echo "=================================="
        
        # 리소스 사용량
        echo -e "${YELLOW}💾 리소스 사용량:${NC}"
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
        
        echo "=================================="
        echo -e "${GREEN}🔄 5초 후 업데이트... (Ctrl+C로 종료)${NC}"
        sleep 5
    done
}

# 요약 모니터링 함수
summary_monitoring() {
    echo -e "${BLUE}📋 요약 모니터링...${NC}"
    echo "=================================="
    
    # 서비스 상태 요약
    echo -e "${YELLOW}📊 서비스 상태 요약:${NC}"
    docker compose -f services/hospital_workers/docker-compose.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    
    echo "=================================="
    
    # 포트 상태 요약
    echo -e "${YELLOW}🔌 포트 상태 요약:${NC}"
    ports=("80" "5173" "8002" "5432" "6379")
    for port in "${ports[@]}"; do
        if netstat -tuln | grep -q ":$port "; then
            echo -e "${GREEN}✅ 포트 $port 사용 중${NC}"
        else
            echo -e "${RED}❌ 포트 $port 연결 없음${NC}"
        fi
    done
    
    echo "=================================="
    
    # 리소스 사용량 요약
    echo -e "${YELLOW}💾 리소스 사용량 요약:${NC}"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemPerc}}"
    
    echo "=================================="
}

# 메인 실행 함수
main() {
    echo -e "${CYAN}🔍 서비스 모니터링 시작...${NC}"
    echo "=================================="

    # 프로젝트 루트 디렉토리로 이동
    cd "$(dirname "$0")/.."

    # 1. Docker 서비스 상태 확인
    echo -e "${BLUE}🐳 Docker 서비스 상태 확인...${NC}"
    if ! command -v docker > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker가 설치되지 않았습니다.${NC}"
        exit 1
    fi

    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker 데몬이 실행되지 않았습니다.${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ Docker 서비스 정상${NC}"
    echo "=================================="

    # 2. 명령행 인수 처리
    if [ $# -eq 0 ]; then
        # 대화형 메뉴
        while true; do
            show_monitoring_menu
            echo -e "${YELLOW}선택하세요 (0-8):${NC} "
            read -r choice
            
            case $choice in
                0)
                    echo -e "${GREEN}👋 모니터링을 종료합니다.${NC}"
                    exit 0
                    ;;
                1)
                    monitor_service "page-server" "Page Server"
                    ;;
                2)
                    monitor_service "api-server" "API Server"
                    ;;
                3)
                    monitor_service "db-server" "Database Server"
                    ;;
                4)
                    monitor_service "nginx" "Nginx"
                    ;;
                5)
                    monitor_service "redis" "Redis"
                    ;;
                6)
                    # 전체 서비스 모니터링
                    for service in "${SERVICES[@]}"; do
                        if [ "$service" != "all" ]; then
                            monitor_service "$service" "$service"
                        fi
                    done
                    monitor_ports
                    monitor_http_connections
                    monitor_database
                    monitor_redis
                    monitor_resources
                    monitor_network
                    monitor_api_endpoints
                    ;;
                7)
                    continuous_monitoring
                    ;;
                8)
                    summary_monitoring
                    ;;
                *)
                    echo -e "${RED}❌ 잘못된 선택입니다. 0-8 중에서 선택하세요.${NC}"
                    ;;
            esac
            
            if [ $choice -ne 7 ]; then
                echo "=================================="
                echo -e "${GREEN}✅ 모니터링 완료!${NC}"
                echo "=================================="
                echo -e "${CYAN}💡 서비스 운영: ./scripts/ensure_services_operated.sh${NC}"
                echo -e "${CYAN}💡 서비스 중지: ./scripts/ensure_service_shutdowned.sh${NC}"
            fi
        done
    else
        # 명령행 인수로 실행
        case $1 in
            --continuous)
                continuous_monitoring
                ;;
            --summary)
                summary_monitoring
                ;;
            --detailed)
                # 상세 모니터링
                for service in "${SERVICES[@]}"; do
                    if [ "$service" != "all" ]; then
                        monitor_service "$service" "$service"
                    fi
                done
                monitor_ports
                monitor_http_connections
                monitor_database
                monitor_redis
                monitor_resources
                monitor_network
                monitor_api_endpoints
                ;;
            *)
                echo -e "${RED}❌ 잘못된 옵션입니다.${NC}"
                echo "사용법: $0 [--continuous|--summary|--detailed]"
                exit 1
                ;;
        esac
        
        echo "=================================="
        echo -e "${GREEN}✅ 모니터링 완료!${NC}"
        echo "=================================="
    fi
}

# 스크립트 실행
main "$@"
