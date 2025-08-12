#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏥 병원 근무자 관리 시스템 - ensure_services_operated.py Unit Test

이 테스트는 ServiceManager 클래스의 모든 기능을 검증합니다.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.ensure_services_operated import ServiceManager, Colors


class TestColors(unittest.TestCase):
    """Colors 클래스 테스트"""
    
    def test_colors_defined(self):
        """색상 상수들이 정의되어 있는지 확인"""
        self.assertTrue(hasattr(Colors, 'RED'))
        self.assertTrue(hasattr(Colors, 'GREEN'))
        self.assertTrue(hasattr(Colors, 'YELLOW'))
        self.assertTrue(hasattr(Colors, 'BLUE'))
        self.assertTrue(hasattr(Colors, 'PURPLE'))
        self.assertTrue(hasattr(Colors, 'CYAN'))
        self.assertTrue(hasattr(Colors, 'NC'))
    
    def test_colors_are_strings(self):
        """색상 상수들이 문자열인지 확인"""
        self.assertIsInstance(Colors.RED, str)
        self.assertIsInstance(Colors.GREEN, str)
        self.assertIsInstance(Colors.YELLOW, str)
        self.assertIsInstance(Colors.BLUE, str)
        self.assertIsInstance(Colors.PURPLE, str)
        self.assertIsInstance(Colors.CYAN, str)
        self.assertIsInstance(Colors.NC, str)


class TestServiceManager(unittest.TestCase):
    """ServiceManager 클래스 테스트"""
    
    def setUp(self):
        """테스트 전 설정"""
        # 테스트용 임시 디렉토리 생성
        self.test_project_root = Path("/tmp/test_hospital_workers")
        self.test_project_root.mkdir(exist_ok=True)
        
        # 테스트용 Docker Compose 파일 생성
        self.test_compose_file = self.test_project_root / "servers" / "docker-compose.dev.yml"
        self.test_compose_file.parent.mkdir(parents=True, exist_ok=True)
        self.test_compose_file.write_text("version: '3.8'")
        
        # ServiceManager 인스턴스 생성 (모킹)
        with patch.object(ServiceManager, '__init__', return_value=None):
            self.manager = ServiceManager()
            self.manager.script_dir = Path("/tmp/test_scripts")
            self.manager.project_root = self.test_project_root
            self.manager.compose_file = self.test_compose_file
            self.manager.is_windows = False
            self.manager.services = {
                "page-server": "Page Server (Next.js)",
                "api-server": "API Server (FastAPI)",
                "db-server": "Database Server (PostgreSQL)",
                "nginx": "Nginx (Reverse Proxy)",
                "redis": "Redis (Cache)"
            }
    
    def tearDown(self):
        """테스트 후 정리"""
        import shutil
        if self.test_project_root.exists():
            shutil.rmtree(self.test_project_root)
    
    def test_init_attributes(self):
        """초기화 시 속성들이 올바르게 설정되는지 확인"""
        manager = ServiceManager()
        self.assertIsInstance(manager.script_dir, Path)
        self.assertIsInstance(manager.project_root, Path)
        self.assertIsInstance(manager.compose_file, Path)
        self.assertIsInstance(manager.is_windows, bool)
        self.assertIsInstance(manager.services, dict)
        self.assertEqual(len(manager.services), 5)
    
    def test_services_definition(self):
        """서비스 정의가 올바른지 확인"""
        expected_services = {
            "page-server", "api-server", "db-server", "nginx", "redis"
        }
        self.assertEqual(set(self.manager.services.keys()), expected_services)
    
    @patch('subprocess.run')
    def test_run_command_success(self, mock_run):
        """명령어 실행 성공 테스트"""
        # Mock 설정
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "success"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        returncode, stdout, stderr = self.manager.run_command("test command")
        
        self.assertEqual(returncode, 0)
        self.assertEqual(stdout, "success")
        self.assertEqual(stderr, "")
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_run_command_failure(self, mock_run):
        """명령어 실행 실패 테스트"""
        # Mock 설정
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error"
        mock_run.return_value = mock_result
        
        returncode, stdout, stderr = self.manager.run_command("test command")
        
        self.assertEqual(returncode, 1)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "error")
    
    @patch('subprocess.run')
    def test_check_docker_success(self, mock_run):
        """Docker 상태 확인 성공 테스트"""
        # Mock 설정
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Docker version 20.10.0"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.manager.check_docker()
        self.assertTrue(result)
    
    @patch('subprocess.run')
    def test_check_docker_not_installed(self, mock_run):
        """Docker 미설치 테스트"""
        # Mock 설정
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "command not found"
        mock_run.return_value = mock_result
        
        result = self.manager.check_docker()
        self.assertFalse(result)
    
    def test_check_compose_file_exists(self):
        """Docker Compose 파일 존재 확인 테스트"""
        result = self.manager.check_compose_file()
        self.assertTrue(result)
    
    def test_check_compose_file_not_exists(self):
        """Docker Compose 파일 미존재 테스트"""
        self.manager.compose_file = Path("/nonexistent/file.yml")
        result = self.manager.check_compose_file()
        self.assertFalse(result)
    
    @patch('subprocess.run')
    def test_build_service_success(self, mock_run):
        """서비스 빌드 성공 테스트"""
        # Mock 설정
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Successfully built"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.manager.build_service("test-service")
        self.assertTrue(result)
    
    @patch('subprocess.run')
    def test_build_service_failure(self, mock_run):
        """서비스 빌드 실패 테스트"""
        # Mock 설정
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Build failed"
        mock_run.return_value = mock_result
        
        result = self.manager.build_service("test-service")
        self.assertFalse(result)
    
    @patch('subprocess.run')
    def test_run_service_success(self, mock_run):
        """서비스 실행 성공 테스트"""
        # Mock 설정
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Started"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.manager.run_service("test-service")
        self.assertTrue(result)
    
    @patch('subprocess.run')
    def test_stop_service_success(self, mock_run):
        """서비스 중지 성공 테스트"""
        # Mock 설정
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Stopped"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.manager.stop_service("test-service")
        self.assertTrue(result)
    
    @patch('subprocess.run')
    def test_get_service_status_success(self, mock_run):
        """서비스 상태 확인 성공 테스트"""
        # Mock 설정
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '[{"Service": "page-server", "State": "Up"}]'
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        status = self.manager.get_service_status()
        self.assertIn("page-server", status)
        self.assertEqual(status["page-server"], "Up")
    
    @patch('subprocess.run')
    def test_get_service_status_failure(self, mock_run):
        """서비스 상태 확인 실패 테스트"""
        # Mock 설정
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error"
        mock_run.return_value = mock_result
        
        status = self.manager.get_service_status()
        self.assertEqual(status, {})
    
    def test_show_service_status(self):
        """서비스 상태 표시 테스트"""
        # Mock 상태 데이터
        with patch.object(self.manager, 'get_service_status') as mock_get_status:
            mock_get_status.return_value = {
                "page-server": "Up",
                "api-server": "Down"
            }
            
            # stdout 캡처를 위한 StringIO 사용
            from io import StringIO
            import sys
            
            captured_output = StringIO()
            sys.stdout = captured_output
            
            try:
                self.manager.show_service_status()
                output = captured_output.getvalue()
                
                # 출력에 서비스 상태가 포함되어 있는지 확인
                self.assertIn("page-server", output)
                self.assertIn("api-server", output)
                self.assertIn("Up", output)
                self.assertIn("Down", output)
            finally:
                sys.stdout = sys.__stdout__
    
    @patch.object(ServiceManager, 'test_services')
    @patch.object(ServiceManager, 'build_service')
    @patch.object(ServiceManager, 'run_service')
    def test_run_all_services_success(self, mock_run, mock_build, mock_test):
        """전체 서비스 실행 성공 테스트"""
        # Mock 설정
        mock_test.return_value = True
        mock_build.return_value = True
        mock_run.return_value = True
        
        result = self.manager.run_all_services()
        self.assertTrue(result)
        
        # 각 메서드가 호출되었는지 확인
        mock_test.assert_called_once()
        mock_build.assert_called_once_with("")
        mock_run.assert_called_once_with("")
    
    @patch.object(ServiceManager, 'test_services')
    def test_run_all_services_test_failure(self, mock_test):
        """전체 서비스 실행 시 테스트 실패 테스트"""
        # Mock 설정
        mock_test.return_value = False
        
        result = self.manager.run_all_services()
        self.assertFalse(result)
    
    @patch.object(ServiceManager, 'test_services')
    @patch.object(ServiceManager, 'build_service')
    def test_run_single_service_success(self, mock_build, mock_test):
        """단일 서비스 실행 성공 테스트"""
        # Mock 설정
        mock_test.return_value = True
        mock_build.return_value = True
        
        with patch.object(self.manager, 'run_service') as mock_run:
            mock_run.return_value = True
            
            result = self.manager.run_single_service("page-server")
            self.assertTrue(result)
            
            # 각 메서드가 호출되었는지 확인
            mock_test.assert_called_once()
            mock_build.assert_called_once_with("page-server")
            mock_run.assert_called_once_with("page-server")
    
    def test_run_single_service_invalid_service(self):
        """잘못된 서비스명으로 실행 시도 테스트"""
        result = self.manager.run_single_service("invalid-service")
        self.assertFalse(result)
    
    @patch('subprocess.run')
    def test_stop_all_services_success(self, mock_run):
        """모든 서비스 중지 성공 테스트"""
        # Mock 설정
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Stopped all services"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.manager.stop_all_services()
        self.assertTrue(result)
    
    def test_test_services_file_structure(self):
        """서비스 테스트 - 파일 구조 테스트"""
        # 필요한 파일들이 존재하는 경우
        result = self.manager.test_services()
        self.assertTrue(result)
    
    def test_test_services_missing_files(self):
        """서비스 테스트 - 파일 누락 테스트"""
        # 임시로 파일을 삭제
        import tempfile
        temp_file = self.test_compose_file.parent / "temp.yml"
        temp_file.write_text("temp")
        
        # compose_file을 임시 파일로 변경
        original_compose_file = self.manager.compose_file
        self.manager.compose_file = temp_file
        
        try:
            result = self.manager.test_services()
            self.assertFalse(result)
        finally:
            # 원래대로 복구
            self.manager.compose_file = original_compose_file
            temp_file.unlink()
    
    @patch('subprocess.run')
    def test_show_logs_success(self, mock_run):
        """서비스 로그 표시 성공 테스트"""
        # Mock 설정
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Log line 1\nLog line 2"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # stdout 캡처
        from io import StringIO
        import sys
        
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            self.manager.show_logs()
            output = captured_output.getvalue()
            
            # 로그 내용이 출력되었는지 확인
            self.assertIn("Log line 1", output)
            self.assertIn("Log line 2", output)
        finally:
            sys.stdout = sys.__stdout__


class TestIntegration(unittest.TestCase):
    """통합 테스트"""
    
    def test_service_manager_creation(self):
        """ServiceManager 인스턴스 생성 테스트"""
        try:
            manager = ServiceManager()
            self.assertIsInstance(manager, ServiceManager)
        except Exception as e:
            # 실제 환경에서 Docker나 파일이 없을 수 있음
            self.skipTest(f"ServiceManager 생성 실패: {e}")
    
    def test_colors_usage(self):
        """색상 사용 테스트"""
        # 색상이 실제로 사용 가능한지 확인
        test_message = f"{Colors.GREEN}Success{Colors.NC}"
        self.assertIn("Success", test_message)
        self.assertIn(Colors.GREEN, test_message)
        self.assertIn(Colors.NC, test_message)


if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)
