#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏥 병원 근무자 관리 시스템 - 통합 서비스 운영 스크립트

이 스크립트는 다음 기능들을 통합합니다:
- 서비스 운영 (빌드, 실행, 중지)
- 서비스 테스트 (파일 구조, Docker Compose, 연결성)
- 컨테이너 관리 (설치, 빌드, 실행, 중지)
- 모니터링 및 상태 확인

사용법:
    python ensure_services_operated.py [옵션]
    
옵션:
    --all              : 전체 서비스 실행
    --page-server      : Page Server만 실행
    --api-server       : API Server만 실행
    --db-server        : Database Server만 실행
    --nginx            : Nginx만 실행
    --redis            : Redis만 실행
    --test             : 서비스 테스트만 실행
    --stop             : 모든 서비스 중지
    --status           : 서비스 상태 확인
    --logs             : 서비스 로그 확인
    --help             : 도움말 표시
"""

import os
import sys
import subprocess
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import platform

# 색상 정의
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

class ServiceManager:
    """병원 근무자 관리 시스템 서비스 관리자"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.project_root = self.script_dir.parent
        self.compose_file = self.project_root / "servers" / "docker-compose.dev.yml"
        self.is_windows = platform.system() == "Windows"
        
        # 서비스 정의 (실제 Docker Compose 서비스명과 일치)
        self.services = {
            "page-server": "Page Server (Next.js)",
            "api-server": "API Server (FastAPI)",
            "db-server": "Database Server (PostgreSQL)",
            "nginx": "Nginx (Reverse Proxy)",
            "redis": "Redis (Cache)"
        }
        
        # 실제 Docker Compose 서비스명 매핑
        self.service_mapping = {
            "servers-page-server-1": "page-server",
            "servers-api-server-1": "api-server", 
            "servers-db-server-1": "db-server",
            "servers-nginx-1": "nginx",
            "servers-redis-1": "redis"
        }
        
        print(f"📁 스크립트 디렉토리: {self.script_dir}")
        print(f"📁 프로젝트 루트: {self.project_root}")
        print(f"📁 Docker Compose 파일: {self.compose_file}")
        print("==================================")
    
    def run_command(self, command: str, check: bool = True, capture_output: bool = False) -> Tuple[int, str, str]:
        """명령어 실행"""
        try:
            if self.is_windows:
                # Windows에서는 cmd 사용
                result = subprocess.run(
                    command, shell=True, check=check, capture_output=capture_output,
                    text=True, encoding='utf-8'
                )
            else:
                # Linux/WSL에서는 bash 사용
                result = subprocess.run(
                    command, shell=True, check=check, capture_output=capture_output,
                    text=True, encoding='utf-8'
                )
            
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return e.returncode, e.stdout or "", e.stderr or ""
        except Exception as e:
            return -1, "", str(e)
    
    def check_docker(self) -> bool:
        """Docker 상태 확인"""
        print("🔍 Docker 설치 및 실행 확인...")
        returncode, stdout, stderr = self.run_command("docker --version", check=False)
        if returncode == 0:
            print("✅ Docker 설치됨")
            
            # Docker 서비스 상태 확인
            returncode, stdout, stderr = self.run_command("docker info", check=False)
            if returncode == 0:
                print("✅ Docker 상태: 정상")
                return True
            else:
                print("❌ Docker 서비스가 실행되지 않음")
                return False
        else:
            print("❌ Docker가 설치되지 않음")
            return False
    
    def check_compose_file(self) -> bool:
        """Docker Compose 파일 존재 확인"""
        if not self.compose_file.exists():
            print(f"❌ Docker Compose 파일을 찾을 수 없습니다: {self.compose_file}")
            return False
        print(f"✅ Docker Compose 파일 확인: {self.compose_file}")
        return True
    
    def build_service(self, service: str) -> bool:
        """서비스 빌드"""
        print(f"🔨 {service} 빌드 중..")
        command = f"docker compose -f {self.compose_file} build {service}"
        returncode, stdout, stderr = self.run_command(command)
        
        if returncode == 0:
            print(f"✅ {service} 빌드 완료")
            return True
        else:
            print(f"❌ {service} 빌드 실패")
            if stderr:
                print(f"오류: {stderr}")
            return False
    
    def run_service(self, service: str) -> bool:
        """서비스 실행"""
        print(f"🚀 {service} 실행 중..")
        command = f"docker compose -f {self.compose_file} up -d {service}"
        returncode, stdout, stderr = self.run_command(command)
        
        if returncode == 0:
            print(f"✅ {service} 실행 완료")
            return True
        else:
            print(f"❌ {service} 실행 실패")
            if stderr:
                print(f"오류: {stderr}")
            return False
    
    def stop_service(self, service: str) -> bool:
        """서비스 중지"""
        print(f"🛑 {service} 중지 중..")
        command = f"docker compose -f {self.compose_file} stop {service}"
        returncode, stdout, stderr = self.run_command(command)
        
        if returncode == 0:
            print(f"✅ {service} 중지 완료")
            return True
        else:
            print(f"❌ {service} 중지 실패")
            if stderr:
                print(f"오류: {stderr}")
            return False
    
    def remove_service(self, service: str) -> bool:
        """서비스 제거"""
        print(f"🗑️ {service} 제거 중..")
        command = f"docker compose -f {self.compose_file} rm -f {service}"
        returncode, stdout, stderr = self.run_command(command)
        
        if returncode == 0:
            print(f"✅ {service} 제거 완료")
            return True
        else:
            print(f"❌ {service} 제거 실패")
            if stderr:
                print(f"오류: {stderr}")
            return False
    
    def get_service_status(self) -> Dict[str, str]:
        """서비스 상태 확인"""
        print("🔍 서비스 상태 확인 중..")
        
        # 방법 1: JSON 형식으로 시도
        command = f"docker compose -f {self.compose_file} ps --format json"
        returncode, stdout, stderr = self.run_command(command, capture_output=True)
        
        status = {}
        if returncode == 0 and stdout:
            try:
                # 여러 줄의 JSON을 개별적으로 파싱
                lines = stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            container = json.loads(line.strip())
                            service_name = container.get('Service', '')
                            state = container.get('State', '')
                            if service_name:
                                status[service_name] = state
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                print(f"⚠️ JSON 파싱 오류: {e}")
        
        # JSON 파싱이 실패하면 일반 텍스트 형식으로 시도
        if not status:
            print("📋 일반 형식으로 서비스 상태 확인 중..")
            command = f"docker compose -f {self.compose_file} ps"
            returncode, stdout, stderr = self.run_command(command, capture_output=True)
            
            if returncode == 0 and stdout:
                lines = stdout.strip().split('\n')
                for line in lines[1:]:  # 헤더 제외
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            # 서비스명 추출 (첫 번째 컬럼)
                            service_name = parts[0]
                            # 상태 확인 (Up, Running 등)
                            if any(status_word in line for status_word in ['Up', 'Running', 'Started']):
                                # 실제 서비스명을 self.service_mapping을 통해 매핑
                                if service_name in self.service_mapping:
                                    mapped_key = self.service_mapping[service_name]
                                    status[mapped_key] = "Up"
                                else:
                                    # 매핑되지 않은 경우 원본 서비스명 사용
                                    status[service_name] = "Up"
        
        return status
    
    def show_service_status(self):
        """서비스 상태 표시"""
        status = self.get_service_status()
        
        print("📋 서비스 상태:")
        print("==================================")
        for service, service_name in self.services.items():
            if service in status:
                state = status[service]
                # running, Up, Started 등 실행 중인 상태를 모두 확인
                if any(running_state in state.lower() for running_state in ['up', 'running', 'started']):
                    print(f"✅ {service_name}: {state}")
                else:
                    print(f"❌ {service_name}: {state}")
            else:
                print(f"⏸️ {service_name}: 중지됨")
        print("==================================")
    
    def run_all_services(self):
        """전체 서비스 실행"""
        print("🚀 전체 서비스 실행 중..")
        
        # 먼저 기본 환경 테스트 실행 (서비스 실행 전)
        print("🧪 기본 환경 테스트 실행 중..")
        if not self.test_basic_environment():
            print("❌ 기본 환경 테스트 실패 - 실행을 중단합니다")
            return False
        
        # 전체 서비스 빌드
        print("🔨 전체 서비스 빌드 중..")
        if not self.build_service(""):
            print("❌ 전체 서비스 빌드 실패")
            return False
        
        # 전체 서비스 실행
        print("🚀 전체 서비스 실행 중..")
        if not self.run_service(""):
            print("❌ 전체 서비스 실행 실패")
            return False
        
        # 서비스 실행 후 상태 확인
        print("🔍 서비스 실행 상태 확인 중..")
        if not self.test_services():
            print("⚠️ 일부 서비스 테스트 실패 - 로그를 확인하세요")
        
        print("✅ 전체 서비스 실행 완료")
        return True
    
    def run_single_service(self, service: str):
        """단일 서비스 실행"""
        if service not in self.services:
            print(f"❌ 알 수 없는 서비스: {service}")
            return False
        
        service_name = self.services[service]
        print(f"🚀 {service_name} 실행 중..")
        
        # 먼저 기본 환경 테스트 실행 (서비스 실행 전)
        print("🧪 기본 환경 테스트 실행 중..")
        if not self.test_basic_environment():
            print("❌ 기본 환경 테스트 실패 - 실행을 중단합니다")
            return False
        
        # 서비스 빌드
        if not self.build_service(service):
            return False
        
        # 서비스 실행
        if not self.run_service(service):
            return False
        
        # 서비스 실행 후 상태 확인
        print("🔍 서비스 실행 상태 확인 중..")
        if not self.test_services():
            print("⚠️ 일부 서비스 테스트 실패 - 로그를 확인하세요")
        
        return True
    
    def stop_all_services(self):
        """모든 서비스 중지"""
        print("🛑 모든 서비스 중지 중..")
        command = f"docker compose -f {self.compose_file} down --remove-orphans"
        returncode, stdout, stderr = self.run_command(command)
        
        if returncode == 0:
            print("✅ 모든 서비스 중지 완료")
            return True
        else:
            print("❌ 서비스 중지 실패")
            if stderr:
                print(f"오류: {stderr}")
            return False
    
    def test_basic_environment(self):
        """기본 환경 테스트 (서비스 실행 전)"""
        print("🧪 기본 환경 테스트 시작...")
        print("==================================")
        
        # 1. 파일 구조 테스트
        print("📁 파일 구조 테스트 중..")
        required_files = [
            self.project_root / "servers" / "docker-compose.dev.yml",
            self.project_root / "servers" / "page_server" / "Dockerfile.dev",
            self.project_root / "servers" / "api_server" / "pyproject.toml",
            self.project_root / "servers" / "page_server" / "nginx" / "nginx.conf"
        ]
        
        for file_path in required_files:
            if file_path.exists():
                print(f"✅ {file_path.name} 존재")
            else:
                print(f"❌ {file_path.name} 없음")
                return False
        
        # 2. Docker Compose 문법 테스트
        print("🔍 Docker Compose 문법 테스트 중..")
        command = f"docker compose -f {self.compose_file} config"
        returncode, stdout, stderr = self.run_command(command, check=False)
        
        if returncode == 0:
            print("✅ Docker Compose 문법 정상")
        else:
            print("❌ Docker Compose 문법 오류")
            if stderr:
                print(f"오류: {stderr}")
            return False
        
        print("==================================")
        print("✅ 기본 환경 테스트 완료")
        return True

    def test_services(self):
        """서비스 테스트 실행 (서비스 실행 후)"""
        print("🧪 서비스 테스트 시작...")
        print("==================================")
        
        # 1. 컨테이너 상태 테스트
        print("🔍 컨테이너 상태 테스트 중..")
        status = self.get_service_status()
        
        print("📋 각 서비스 상태:")
        all_running = True
        for service in self.services.keys():
            if service in status and any(running_state in status[service].lower() for running_state in ['up', 'running', 'started']):
                print(f"✅ {service} 실행 중")
            else:
                print(f"❌ {service} 실행 실패")
                all_running = False
        
        if not all_running:
            print("❌ 일부 서비스 실행 실패")
            return False
        
        print("==================================")
        
        # 2. 포트 연결 테스트
        print("🔍 포트 연결 테스트 중..")
        ports = {
            80: "nginx",
            5173: "page-server",
            8002: "api-server",
            15432: "db-server (외부)",
            16379: "redis (외부)"
        }
        
        for port, service_name in ports.items():
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    print(f"✅ {service_name} (포트 {port}) 연결됨")
                else:
                    print(f"❌ {service_name} (포트 {port}) 연결 실패")
            except Exception as e:
                print(f"⚠️ {service_name} (포트 {port}) 테스트 오류: {e}")
        
        print("==================================")
        print("✅ 서비스 테스트 완료")
        return True
    
    def show_logs(self, service: Optional[str] = None):
        """서비스 로그 확인"""
        if service:
            print(f"📋 {service} 로그:")
            command = f"docker compose -f {self.compose_file} logs --tail=20 {service}"
        else:
            print("📋 전체 서비스 로그:")
            command = f"docker compose -f {self.compose_file} logs --tail=20"
        
        returncode, stdout, stderr = self.run_command(command, capture_output=True)
        
        if returncode == 0 and stdout:
            print(stdout)
        else:
            print("❌ 로그를 가져올 수 없습니다")
            if stderr:
                print(f"오류: {stderr}")
    
    def show_menu(self):
        """대화형 메뉴 표시"""
        while True:
            print(f"{Colors.CYAN}🏥 병원 근무자 관리 시스템 서비스 운영{Colors.NC}")
            print("==================================")
            print(f"{Colors.YELLOW}📋 메뉴 선택:{Colors.NC}")
            print("1. 전체 서비스 실행")
            print("2. 개별 서비스 실행")
            print("3. 서비스 상태 확인")
            print("4. 서비스 테스트")
            print("5. 서비스 로그 확인")
            print("6. 모든 서비스 중지")
            print("0. 종료")
            print("==================================")
            
            try:
                choice = input("선택하세요 (0-6): ").strip()
                
                if choice == "0":
                    print("👋 프로그램을 종료합니다.")
                    break
                elif choice == "1":
                    self.run_all_services()
                elif choice == "2":
                    self.show_service_selection_menu()
                elif choice == "3":
                    self.show_service_status()
                elif choice == "4":
                    self.test_services()
                elif choice == "5":
                    self.show_logs()
                elif choice == "6":
                    self.stop_all_services()
                else:
                    print("❌ 잘못된 선택입니다. 다시 선택해주세요.")
                
                if choice != "0":
                    input("\n계속하려면 Enter를 누르세요...")
                    print("\n" + "="*50 + "\n")
                    
            except KeyboardInterrupt:
                print("\n\n👋 프로그램을 종료합니다.")
                break
            except Exception as e:
                print(f"❌ 오류가 발생했습니다: {e}")
    
    def show_service_selection_menu(self):
        """서비스 선택 메뉴"""
        print(f"{Colors.CYAN}📋 서비스 선택:{Colors.NC}")
        print("==================================")
        
        for i, (service, service_name) in enumerate(self.services.items(), 1):
            print(f"{i}. {service_name}")
        print("0. 뒤로 가기")
        print("==================================")
        
        try:
            choice = input("선택하세요 (0-5): ").strip()
            
            if choice == "0":
                return
            elif choice.isdigit() and 1 <= int(choice) <= 5:
                service_list = list(self.services.keys())
                selected_service = service_list[int(choice) - 1]
                self.run_single_service(selected_service)
            else:
                print("❌ 잘못된 선택입니다.")
                
        except KeyboardInterrupt:
            print("\n뒤로 돌아갑니다.")
        except Exception as e:
            print(f"❌ 오류가 발생했습니다: {e}")

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="🏥 병원 근무자 관리 시스템 - 통합 서비스 운영 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python ensure_services_operated.py --all          # 전체 서비스 실행
  python ensure_services_operated.py --page-server  # Page Server만 실행
  python ensure_services_operated.py --stop         # 모든 서비스 중지
  python ensure_services_operated.py --status       # 서비스 상태 확인
  python ensure_services_operated.py                # 대화형 메뉴
        """
    )
    
    parser.add_argument("--all", action="store_true", help="전체 서비스 실행")
    parser.add_argument("--page-server", action="store_true", help="Page Server만 실행")
    parser.add_argument("--api-server", action="store_true", help="API Server만 실행")
    parser.add_argument("--db-server", action="store_true", help="Database Server만 실행")
    parser.add_argument("--nginx", action="store_true", help="Nginx만 실행")
    parser.add_argument("--redis", action="store_true", help="Redis만 실행")

    parser.add_argument("--stop", action="store_true", help="모든 서비스 중지")
    parser.add_argument("--status", action="store_true", help="서비스 상태 확인")
    parser.add_argument("--logs", action="store_true", help="서비스 로그 확인")
    
    args = parser.parse_args()
    
    # 서비스 매니저 초기화
    manager = ServiceManager()
    
    # Docker 상태 확인
    if not manager.check_docker():
        print("❌ Docker가 실행되지 않았습니다. Docker를 시작한 후 다시 시도해주세요.")
        sys.exit(1)
    
    # Docker Compose 파일 확인
    if not manager.check_compose_file():
        print("❌ Docker Compose 파일을 찾을 수 없습니다.")
        sys.exit(1)
    
    # 명령행 인수 처리
    if args.all:
        manager.run_all_services()
    elif args.page_server:
        manager.run_single_service("page-server")
    elif args.api_server:
        manager.run_single_service("api-server")
    elif args.db_server:
        manager.run_single_service("db-server")
    elif args.nginx:
        manager.run_single_service("nginx")
    elif args.redis:
        manager.run_single_service("redis")

    elif args.stop:
        manager.stop_all_services()
    elif args.status:
        manager.show_service_status()
    elif args.logs:
        manager.show_logs()
    else:
        # 대화형 메뉴 표시
        manager.show_menu()

if __name__ == "__main__":
    main()
