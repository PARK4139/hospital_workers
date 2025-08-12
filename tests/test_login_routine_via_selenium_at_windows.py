"""
Frontend Login Routine Selenium Test
프론트엔드 로그인 기능을 Selenium으로 테스트하는 프로그램입니다.
Windows 환경 설정 기능을 포함하여 제공합니다.
의존성 없이 독립적으로 실행 가능합니다.
"""

import os
import sys
import subprocess
import logging
import time
import requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pytest

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
            logging.FileHandler('logs/frontend_login_test.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
)
logger = logging.getLogger(__name__)

class EnvironmentSetup:
    """Linux/Windows 환경 설정을 위한 클래스"""
    
    def __init__(self):
        self.is_windows = os.name == 'nt'
        self.is_linux = os.name == 'posix'
        self.project_root = Path(__file__).parent.parent
        self.venv_linux_path = self.project_root / ".venv_linux"
        self.venv_windows_path = self.project_root / ".venv_windows"
    
    def setup_environment(self):
        """환경 설정"""
        try:
            if self.is_windows:
                return self.setup_windows_environment()
            elif self.is_linux:
                return self.setup_linux_environment()
            else:
                logger.error("지원하지 않는 운영체제입니다")
                return False
                
        except Exception as e:
            logger.error(f"환경 설정 중 오류: {e}")
            return False
    
    def setup_windows_environment(self):
        """Windows 환경 설정"""
        try:
            # 가상환경 경로 확인
            if not self.venv_windows_path.exists():
                logger.error("Windows 가상환경이 존재하지 않습니다")
                return False
            
            # Python 실행 파일 경로 확인
            python_path = self.get_windows_python_path()
            if not os.path.exists(python_path):
                logger.error(f"Windows Python 실행 파일을 찾을 수 없습니다: {python_path}")
                return False
            
            logger.info("Windows 환경 설정이 완료되었습니다")
            return True
            
        except Exception as e:
            logger.error(f"Windows 환경 설정 중 오류: {e}")
            return False
    
    def setup_linux_environment(self):
        """Linux 환경 설정"""
        try:
            # 가상환경 경로 확인
            if not self.venv_linux_path.exists():
                logger.error("Linux 가상환경이 존재하지 않습니다")
                return False
            
            # Python 실행 파일 경로 확인
            python_path = self.get_linux_python_path()
            if not os.path.exists(python_path):
                logger.error(f"Linux Python 실행 파일을 찾을 수 없습니다: {python_path}")
                return False
            
            logger.info("Linux 환경 설정이 완료되었습니다")
            return True
            
        except Exception as e:
            logger.error(f"Linux 환경 설정 중 오류: {e}")
            return False
    
    def get_windows_python_path(self):
        """Windows 가상환경의 Python 경로 반환"""
        if self.is_windows and self.venv_windows_path.exists():
            return str(self.venv_windows_path / "Scripts" / "python.exe")
        return sys.executable
    
    def get_linux_python_path(self):
        """Linux 가상환경의 Python 경로 반환"""
        if self.is_linux and self.venv_linux_path.exists():
            return str(self.venv_linux_path / "bin" / "python")
        return sys.executable
    
    def get_current_python_path(self):
        """현재 환경에 맞는 Python 경로 반환"""
        if self.is_windows:
            return self.get_windows_python_path()
        elif self.is_linux:
            return self.get_linux_python_path()
        return sys.executable
    
    def run_test_command(self, test_file):
        """현재 환경에서 테스트 명령어 실행"""
        python_path = self.get_current_python_path()
        test_path = self.project_root / "tests" / test_file
        
        if not test_path.exists():
            logger.error(f"테스트 파일을 찾을 수 없습니다: {test_path}")
            return False
        
        logger.info(f"테스트 {test_file} 실행 중... (Python: {python_path})")
        result = subprocess.run([
            python_path, "-m", "pytest", str(test_path), "-v", "-s"
        ], capture_output=True, text=True, cwd=self.project_root)
        
        if result.returncode == 0:
            logger.info(f"테스트 {test_file} 성공")
            return True
        else:
            logger.error(f"테스트 {test_file} 실패: {result.stderr}")
            return False


class ServiceChecker:
    """서비스 상태 확인 및 관리 클래스"""
    
    def __init__(self):
        self.services = {
            'frontend': 'http://localhost:5173',
            'api': 'http://localhost:8002',
            'database': 'localhost:5432'
        }
    
    def check_service_health(self, service_name):
        """서비스 상태 확인"""
        if service_name not in self.services:
            return False
        
        try:
            if service_name in ['frontend', 'api']:
                response = requests.get(self.services[service_name], timeout=5)
                return response.status_code < 500
            elif service_name == 'database':
                # 간단한 포트 체크
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', 5432))
                sock.close()
                return result == 0
        except Exception as e:
            logger.warning(f"서비스 {service_name} 상태 확인 실패: {e}")
            return False
        
        return False
    
    def get_available_services(self):
        """사용 가능한 서비스 목록 반환"""
        available = {}
        for service_name in self.services:
            available[service_name] = self.check_service_health(service_name)
        return available


class TestFrontendLoginRoutine:
    """프론트엔드 로그인 루틴 테스트"""
    
    @pytest.fixture(scope="session")
    def environment_setup(self):
        """환경 설정"""
        setup = EnvironmentSetup()
        setup.setup_environment()
        # 로그인 루틴은 Windows 전용
        if not setup.is_windows:
            pytest.fail("로그인 루틴 테스트는 반드시 Windows 환경에서 실행해야 합니다")
        return setup
    
    @pytest.fixture(scope="session")
    def service_checker(self):
        """서비스 상태 확인기"""
        return ServiceChecker()
    
    @pytest.fixture(scope="session", autouse=False)
    def driver(self, environment_setup):
        """Chrome WebDriver 설정 - 브라우저 자동 종료 완전 방지"""
        """Chrome WebDriver 설정 - 브라우저 자동 종료 방지"""
        logger.info("Chrome WebDriver 설정 시작...")
        
        try:
            chrome_options = Options()
            # 테스트 종료 후에도 Chrome 창 유지
            try:
                chrome_options.add_experimental_option("detach", True)
            except Exception:
                pass
            
            # 환경에 따라 headless 모드 설정
            if environment_setup.is_windows:
                # Windows 환경에서는 headless 모드 비활성화 (브라우저 창 표시)
                logger.info("Windows 환경: headless 모드 비활성화 (브라우저 창 표시)")
                chrome_options.add_argument("--window-size=1920,1080")
                # Windows에서 브라우저 자동 종료 방지
                chrome_options.add_argument("--disable-background-timer-throttling")
                chrome_options.add_argument("--disable-backgrounding-occluded-windows")
                chrome_options.add_argument("--disable-renderer-backgrounding")
            elif environment_setup.is_linux:
                # Linux 환경에서는 headless 모드 활성화
                logger.info("Linux 환경: headless 모드 활성화")
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--window-size=1920,1080")
            
            # 공통 옵션
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-web-security")
            # Windows에서 DevToolsActivePort 오류 방지: user-data-dir을 OS별 유효 경로로 설정
            try:
                import tempfile, os as _os
                if environment_setup.is_windows:
                    _ud = _os.path.join(tempfile.gettempdir(), "chrome-test-profile")
                else:
                    _ud = "/tmp/chrome-test"
                chrome_options.add_argument(f"--user-data-dir={_ud}")
                chrome_options.add_argument("--remote-allow-origins=*")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--no-first-run")
                chrome_options.add_argument("--no-default-browser-check")
            except Exception:
                pass
            # 브라우저 자동 종료 방지
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.implicitly_wait(10)
            
            logger.info("Chrome WebDriver 설정 완료")
            logger.info("🔒 브라우저 자동 종료 방지 옵션 적용됨")
            yield driver
            
        except Exception as e:
            logger.error(f"Chrome WebDriver 설정 실패: {e}")
            raise
        finally:
            # Chrome 브라우저를 계속 열린 상태로 유지
            logger.info("Chrome WebDriver를 열린 상태로 유지합니다")
            logger.info("💡 브라우저를 수동으로 종료하려면 브라우저 창을 닫으세요.")
            logger.info("🚫 pytest fixture 정리로 인한 자동 종료 방지")
            logger.info("🛡️ Chrome 옵션으로 자동 종료 방지")
            # driver.quit() 호출하지 않음 - 브라우저 창 유지
            # pytest가 fixture를 정리해도 브라우저는 유지
            
            # 추가 보호: 브라우저 프로세스 유지
            try:
                import psutil
                current_pid = driver.service.process.pid
                logger.info(f"🔒 Chrome 프로세스 PID: {current_pid} 유지")
                logger.info("🛡️ pytest 종료 후에도 브라우저 프로세스가 계속 실행됩니다")
            except Exception as e:
                logger.warning(f"프로세스 정보 확인 실패: {e}")
    
    def test_environment_setup(self, environment_setup):
        """환경 설정 테스트"""
        if not environment_setup.is_windows and not environment_setup.is_linux:
            pytest.skip("지원하지 않는 운영체제입니다")
        
        logger.info("환경 설정 테스트 시작...")
        
        # 가상환경 존재 확인
        if environment_setup.is_windows:
            assert environment_setup.venv_windows_path.exists(), "Windows 가상환경이 생성되지 않았습니다"
        elif environment_setup.is_linux:
            assert environment_setup.venv_linux_path.exists(), "Linux 가상환경이 생성되지 않았습니다"
        
        # Python 실행 파일 존재 확인
        python_path = environment_setup.get_current_python_path()
        assert os.path.exists(python_path), f"Python 실행 파일을 찾을 수 없습니다: {python_path}"
        
        # 필요한 패키지 설치 확인
        try:
            import selenium
            import pytest
            import webdriver_manager
            import requests
            logger.info("모든 필요한 패키지가 설치되어 있습니다")
        except ImportError as e:
            pytest.fail(f"필요한 패키지가 설치되지 않았습니다: {e}")
        
        logger.info("환경 설정 테스트 통과")
    
    def test_service_availability(self, service_checker):
        """서비스 가용성 테스트"""
        logger.info("서비스 가용성 테스트 시작...")
        
        available_services = service_checker.get_available_services()
        
        for service_name, is_available in available_services.items():
            if is_available:
                logger.info(f"✅ 서비스 {service_name} 사용 가능")
            else:
                logger.warning(f"⚠️ 서비스 {service_name} 사용 불가")
        
        # 모든 서비스가 사용 불가능해도 테스트는 계속 진행
        logger.info("서비스 가용성 테스트 완료 (서비스 없이도 테스트 계속)")
    
    def wait_for_element(self, driver, by, value, timeout=10):
        """요소가 나타날 때까지 대기"""
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            logger.error(f"요소 대기 실패 ({by}={value}): {e}")
            return None
    
    def safe_click(self, driver, element):
        """안전한 클릭 수행"""
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            element.click()
            return True
        except Exception as e:
            logger.error(f"클릭 실패: {e}")
            return False
    
    def test_page_load_and_title(self, driver, service_checker):
        """페이지 로드 및 제목 테스트"""
        logger.info("페이지 로드 및 제목 테스트 시작...")
        
        # 서비스 상태 확인
        frontend_available = service_checker.check_service_health('frontend')
        
        if not frontend_available:
            logger.warning("프론트엔드 서비스가 실행되지 않음 - 실제 서비스 시작 시도")
            
            # 실제 서비스 시작 시도
            try:
                logger.info("🚀 실제 frontend 서비스 연결 시도...")
                driver.get("http://localhost:5173")
                time.sleep(3)
                
                # 페이지 로드 확인
                title = driver.title
                logger.info(f"실제 페이지 제목: {title}")
                
                if title and title != "Mock Login Page":
                    logger.info("✅ 실제 frontend 서비스에 연결됨!")
                    frontend_available = True
                else:
                    logger.warning("⚠️ 실제 서비스 연결 실패 - 모의 테스트 진행")
                    
            except Exception as e:
                logger.warning(f"실제 서비스 연결 시도 실패: {e}")
                logger.error("프론트엔드 서비스가 필요합니다. 모의 페이지 사용은 금지됩니다.")
                pytest.fail("프론트엔드 서비스(5173)가 실행 중이어야 합니다. 모의 페이지는 사용하지 않습니다.")
        
        if frontend_available:
            try:
                # 실제 서비스 테스트
                # 프론트엔드는 현재 루트 경로(`/`)에 로그인 폼을 렌더링하므로 해당 경로를 사용
                driver.get("http://localhost:5173/")
                time.sleep(2)
                
                title = driver.title
                logger.info(f"실제 페이지 제목: {title}")
                
                login_form = self.wait_for_element(driver, By.TAG_NAME, "form")
                if login_form:
                    driver.save_screenshot("tests/results/01_real_page_load_success.png")
                    logger.info("📸 실제 페이지 로드 성공 스크린샷 저장")
                    logger.info("실제 페이지 로드 테스트 통과")
                else:
                    driver.save_screenshot("tests/results/02_real_page_load_failed.png")
                    pytest.fail("실제 로그인 폼을 찾을 수 없습니다")
                    
            except Exception as e:
                driver.save_screenshot("tests/results/02_real_page_load_failed.png")
                logger.error(f"실제 페이지 로드 테스트 실패: {e}")
                pytest.fail(f"실제 페이지 로드 테스트 실패: {e}")
    
    def test_login_form_structure(self, driver):
        """로그인 폼 구조 테스트"""
        logger.info("로그인 폼 구조 테스트 시작...")
        
        try:
            # 이메일 입력 필드 확인
            email_input = self.wait_for_element(driver, By.NAME, "email")
            if not email_input:
                driver.save_screenshot("tests/results/03_login_form_structure_failed.png")
                pytest.fail("이메일 입력 필드를 찾을 수 없습니다")
            
            # 비밀번호 입력 필드 확인
            password_input = self.wait_for_element(driver, By.NAME, "password")
            if not password_input:
                driver.save_screenshot("tests/results/03_login_form_structure_failed.png")
                pytest.fail("비밀번호 입력 필드를 찾을 수 없습니다")
            
            # 로그인 버튼 확인
            login_button = self.wait_for_element(driver, By.XPATH, "//button[@type='submit']")
            if not login_button:
                driver.save_screenshot("tests/results/03_login_form_structure_failed.png")
                pytest.fail("로그인 버튼을 찾을 수 없습니다")
            
            logger.info("로그인 폼 구조 테스트 통과")
            
        except Exception as e:
            driver.save_screenshot("tests/results/03_login_form_structure_failed.png")
            logger.error(f"로그인 폼 구조 테스트 실패: {e}")
            pytest.fail(f"로그인 폼 구조 테스트 실패: {e}")
    
    def test_form_interaction(self, driver):
        """폼 상호작용 테스트 (의존성 없음)"""
        logger.info("폼 상호작용 테스트 시작...")
        
        try:
            # 이메일 입력
            email_input = self.wait_for_element(driver, By.NAME, "email")
            if email_input:
                email_input.clear()
                email_input.send_keys("test@example.com")
                logger.info("이메일 입력 성공")
            
            # 비밀번호 입력
            password_input = self.wait_for_element(driver, By.NAME, "password")
            if password_input:
                password_input.clear()
                password_input.send_keys("testpassword")
                logger.info("비밀번호 입력 성공")
            
            # 입력값 확인
            if email_input and password_input:
                email_value = email_input.get_attribute("value")
                password_value = password_input.get_attribute("value")
                
                assert email_value == "test@example.com", f"이메일 입력값 불일치: {email_value}"
                assert password_value == "testpassword", f"비밀번호 입력값 불일치: {password_value}"
                
                driver.save_screenshot("tests/results/04_form_interaction_success.png")
                logger.info("폼 상호작용 테스트 통과")
            else:
                pytest.fail("폼 요소를 찾을 수 없습니다")
                
        except Exception as e:
            driver.save_screenshot("tests/results/04_form_interaction_failed.png")
            logger.error(f"폼 상호작용 테스트 실패: {e}")
            pytest.fail(f"폼 상호작용 테스트 실패: {e}")
    
    def test_browser_functionality(self, driver):
        """브라우저 기능 테스트 (의존성 없음)"""
        logger.info("브라우저 기능 테스트 시작...")
        
        try:
            # 브라우저 창 크기 변경 테스트
            original_size = driver.get_window_size()
            logger.info(f"원래 창 크기: {original_size}")
            
            # 다양한 창 크기로 테스트
            test_sizes = [(1024, 768), (1366, 768), (1920, 1080)]
            
            for width, height in test_sizes:
                driver.set_window_size(width, height)
                time.sleep(1)
                current_size = driver.get_window_size()
                logger.info(f"창 크기 변경: {current_size}")
                
                # 스크린샷 저장
                driver.save_screenshot(f"tests/results/05_browser_size_{width}x{height}.png")
            
            # 원래 크기로 복원
            driver.set_window_size(original_size['width'], original_size['height'])
            
            # 페이지 새로고침 테스트
            driver.refresh()
            time.sleep(2)
            
            driver.save_screenshot("tests/results/06_browser_refresh_test.png")
            logger.info("브라우저 기능 테스트 통과")
            
        except Exception as e:
            driver.save_screenshot("tests/results/06_browser_functionality_failed.png")
            logger.error(f"브라우저 기능 테스트 실패: {e}")
            pytest.fail(f"브라우저 기능 테스트 실패: {e}")
    
    def test_selenium_capabilities(self, driver):
        """Selenium 기능 테스트 (의존성 없음)"""
        logger.info("Selenium 기능 테스트 시작...")
        
        try:
            # JavaScript 실행 테스트
            result = driver.execute_script("return 'Selenium Test Success';")
            assert result == "Selenium Test Success", f"JavaScript 실행 결과 불일치: {result}"
            
            # 페이지 소스 확인
            page_source = driver.page_source
            assert len(page_source) > 0, "페이지 소스가 비어있습니다"
            
            # 쿠키 관리 테스트
            driver.add_cookie({'name': 'test_cookie', 'value': 'test_value'})
            cookies = driver.get_cookies()
            test_cookie = next((c for c in cookies if c['name'] == 'test_cookie'), None)
            assert test_cookie is not None, "테스트 쿠키를 찾을 수 없습니다"
            
            driver.save_screenshot("tests/results/07_selenium_capabilities_test.png")
            logger.info("Selenium 기능 테스트 통과")
            
        except Exception as e:
            driver.save_screenshot("tests/results/07_selenium_capabilities_failed.png")
            logger.error(f"Selenium 기능 테스트 실패: {e}")
            pytest.fail(f"Selenium 기능 테스트 실패: {e}")

    def test_login_with_valid_credentials(self, driver):
        """유효한 자격 증명으로 실제 로그인 제출 테스트 (foo@foo / foo)"""
        logger.info("유효한 자격증명 로그인 테스트 시작...")
        # 1) 테스트 계정 보장
        try:
            resp = requests.post("http://localhost/api/auth/create-test-account", timeout=10)
            logger.info(f"테스트 계정 보장 응답: {resp.status_code} {resp.text[:200]}")
        except Exception as e:
            logger.warning(f"테스트 계정 보장 실패(무시 가능): {e}")

        # 2) 로그인 페이지 접속
        driver.get("http://localhost:5173/")
        WebDriverWait(driver, 10).until(lambda d: "Hospital" in d.title or d.find_elements(By.TAG_NAME, "form"))

        # 3) 폼 입력 및 제출
        email_input = self.wait_for_element(driver, By.NAME, "email")
        password_input = self.wait_for_element(driver, By.NAME, "password")
        assert email_input and password_input, "로그인 입력 요소를 찾을 수 없습니다"

        email_input.clear(); email_input.send_keys("foo@foo")
        password_input.clear(); password_input.send_keys("foo")

        submit_btn = self.wait_for_element(driver, By.XPATH, "//button[@type='submit']")
        assert submit_btn, "로그인 버튼을 찾을 수 없습니다"
        self.safe_click(driver, submit_btn)

        # 4) 성공 메시지 확인
        try:
            success_el = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'로그인 성공')]"))
            )
            assert success_el is not None, "로그인 성공 메시지를 찾을 수 없습니다"
            driver.save_screenshot("tests/results/09_login_submit_success.png")
            logger.info("유효한 자격증명 로그인 테스트 통과")
        except Exception as e:
            driver.save_screenshot("tests/results/09_login_submit_failed.png")
            logger.error(f"로그인 제출 테스트 실패: {e}")
            pytest.fail(f"로그인 제출 테스트 실패: {e}")
    
    def test_comprehensive_validation(self, driver, environment_setup, service_checker):
        """종합 검증 테스트"""
        logger.info("종합 검증 테스트 시작...")
        
        try:
            # 환경 정보 수집
            env_info = {
                'os': 'Windows' if environment_setup.is_windows else 'Linux' if environment_setup.is_linux else 'Unknown',
                'python_path': environment_setup.get_current_python_path(),
                'services': service_checker.get_available_services()
            }
            
            logger.info(f"환경 정보: {env_info}")
            
            # 브라우저 정보 수집
            browser_info = {
                'user_agent': driver.execute_script("return navigator.userAgent;"),
                'window_size': driver.get_window_size(),
                'current_url': driver.current_url
            }
            
            logger.info(f"브라우저 정보: {browser_info}")
            
            # 최종 스크린샷
            driver.save_screenshot("tests/results/08_comprehensive_test_result.png")
            
            # 테스트 요약
            logger.info("🎉 모든 테스트가 완료되었습니다!")
            logger.info(f"🔧 환경: {env_info['os']}")
            logger.info(f"🐍 Python: {env_info['python_path']}")
            logger.info(f"🌐 서비스 상태: {env_info['services']}")
            logger.info("🔒 Chrome 브라우저를 열린 상태로 유지합니다.")
            logger.info("💡 브라우저를 수동으로 종료하려면 브라우저 창을 닫으세요.")
            logger.info("🚫 pytest fixture scope를 'session'으로 설정하여 브라우저가 자동으로 닫히지 않습니다.")
            
            # 최종 보호: 브라우저 강제 유지
            logger.info("🛡️ 브라우저 강제 유지 모드 활성화")
            logger.info("💡 이제 pytest가 종료되어도 Chrome 브라우저가 계속 열려있습니다!")
            logger.info("🚪 브라우저를 닫으려면 직접 창을 닫아주세요.")
            
            # 무한 대기로 브라우저 유지 (사용자가 직접 닫을 때까지)
            try:
                logger.info("⏳ 브라우저 유지를 위해 대기 중... (Ctrl+C로 중단 가능)")
                while True:
                    time.sleep(1)
                    # 브라우저가 여전히 열려있는지 확인
                    try:
                        current_title = driver.title
                        if not current_title:
                            break
                    except:
                        break
            except KeyboardInterrupt:
                logger.info("👋 사용자에 의해 테스트가 중단되었습니다.")
                logger.info("🔒 브라우저는 여전히 열려있습니다.")
            
        except Exception as e:
            logger.error(f"❌ 종합 검증 테스트 실패: {e}")
            driver.save_screenshot("tests/results/08_comprehensive_test_failed.png")
            pytest.fail(f"종합 검증 테스트 실패: {e}")


if __name__ == "__main__":
    # 테스트 실행
    pytest.main([__file__, "-v", "-s"])
