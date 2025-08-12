'use client';

import { useState } from 'react';
import Image from 'next/image';

// API 기본 URL
const API_BASE_URL = 'http://localhost/api';

export default function Home() {
  const [activeTab, setActiveTab] = useState('login');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  // 로그인 폼 상태
  const [loginForm, setLoginForm] = useState({
    email: '',
    password: ''
  });

  // 회원가입 폼 상태
  const [signupForm, setSignupForm] = useState({
    firstName: '',
    lastName: '',
    email: '',
    department: '',
    password: '',
    confirmPassword: '',
    agreeTerms: false
  });

  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
    setMessage('');
  };

  // 로그인 처리
  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: loginForm.email,
          password: loginForm.password
        })
      });

      const data = await response.json();

      if (response.ok) {
        setMessage('로그인 성공!');
        // 로그인 성공 후 처리 (예: 토큰 저장, 리다이렉트 등)
        console.log('Login successful:', data);
      } else {
        setMessage(data.detail || '로그인에 실패했습니다.');
      }
    } catch (error) {
      setMessage('로그인 중 오류가 발생했습니다.');
      console.error('Login error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 회원가입 처리
  const handleSignupSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (signupForm.password !== signupForm.confirmPassword) {
      setMessage('비밀번호가 일치하지 않습니다.');
      return;
    }

    if (!signupForm.agreeTerms) {
      setMessage('이용약관에 동의해주세요.');
      return;
    }

    setIsLoading(true);
    setMessage('');

    try {
      const response = await fetch(`${API_BASE_URL}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          first_name: signupForm.firstName,
          last_name: signupForm.lastName,
          email: signupForm.email,
          department: signupForm.department,
          password: signupForm.password
        })
      });

      const data = await response.json();

      if (response.ok) {
        setMessage('회원가입이 완료되었습니다!');
        // 폼 초기화
        setSignupForm({
          firstName: '',
          lastName: '',
          email: '',
          department: '',
          password: '',
          confirmPassword: '',
          agreeTerms: false
        });
        // 로그인 탭으로 이동
        setActiveTab('login');
      } else {
        setMessage(data.detail || '회원가입에 실패했습니다.');
      }
    } catch (error) {
      setMessage('회원가입 중 오류가 발생했습니다.');
      console.error('Signup error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* 헤더 */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-indigo-600">🏥 병원 근무자 관리</h1>
              </div>
            </div>
            <nav className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-4">
                <button
                  onClick={() => handleTabChange('login')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === 'login'
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  로그인
                </button>
                <button
                  onClick={() => handleTabChange('signup')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === 'signup'
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  회원가입
                </button>
                <button
                  onClick={() => handleTabChange('location')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === 'location'
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  병실 위치
                </button>
              </div>
            </nav>
          </div>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <main className="max-w-7xl mx-auto py-6 sm:py-12 px-4 sm:px-6 lg:px-8">
        {/* 환영 메시지 */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            병원 근무자 관리 시스템에 오신 것을 환영합니다
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            효율적인 병원 근무 관리를 위한 통합 플랫폼입니다. 
            로그인하여 업무를 시작하거나 새로운 계정을 만들어보세요.
          </p>
        </div>

        {/* 탭 콘텐츠 */}
        <div className="bg-white rounded-lg shadow-xl p-8">
          {activeTab === 'login' && (
            <div className="max-w-md mx-auto">
              <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">로그인</h3>
              <form className="space-y-6" onSubmit={handleLoginSubmit}>
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    이메일
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={loginForm.email}
                    onChange={(e) => setLoginForm({...loginForm, email: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-black placeholder-gray-500"
                    placeholder="your.email@hospital.com"
                    required
                  />
                </div>
                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                    비밀번호
                  </label>
                  <input
                    type="password"
                    id="password"
                    name="password"
                    value={loginForm.password}
                    onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-black placeholder-gray-500"
                    placeholder="••••••••"
                    required
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <input
                      id="remember-me"
                      name="remember-me"
                      type="checkbox"
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900">
                      로그인 상태 유지
                    </label>
                  </div>
                  <div className="text-sm">
                    <a href="#" className="font-medium text-indigo-600 hover:text-indigo-500">
                      비밀번호 찾기
                    </a>
                  </div>
                </div>
                <div>
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? '로그인 중...' : '로그인'}
                  </button>
                </div>
                
                {/* 메시지 표시 */}
                {message && (
                  <div className={`mt-4 p-3 rounded-md text-sm ${
                    message.includes('성공') || message.includes('완료') 
                      ? 'bg-green-100 text-green-700 border border-green-200' 
                      : 'bg-red-100 text-red-700 border border-red-200'
                  }`}>
                    {message}
                  </div>
                )}
                <div className="mt-6">
                  <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                      <div className="w-full border-t border-gray-300" />
                    </div>
                    <div className="relative flex justify-center text-sm">
                      <span className="px-2 bg-white text-gray-500">또는</span>
                    </div>
                  </div>
                  <div className="mt-6">
                    <button
                      type="button"
                      className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                      </svg>
                      Google로 로그인
                    </button>
                  </div>
                </div>
              </form>
            </div>
          )}

          {activeTab === 'signup' && (
            <div className="max-w-md mx-auto">
              <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">회원가입</h3>
              <form className="space-y-6" onSubmit={handleSignupSubmit}>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-2">
                      이름
                    </label>
                    <input
                      type="text"
                      id="firstName"
                      name="firstName"
                      value={signupForm.firstName}
                      onChange={(e) => setSignupForm({...signupForm, firstName: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-black placeholder-gray-500"
                      placeholder="홍"
                      required
                    />
                  </div>
                  <div>
                    <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 mb-2">
                      성
                    </label>
                    <input
                      type="text"
                      id="lastName"
                      name="lastName"
                      value={signupForm.lastName}
                      onChange={(e) => setSignupForm({...signupForm, lastName: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-black placeholder-gray-500"
                      placeholder="길동"
                      required
                    />
                  </div>
                </div>
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    이메일
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={signupForm.email}
                    onChange={(e) => setSignupForm({...signupForm, email: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-black placeholder-gray-500"
                    placeholder="your.email@hospital.com"
                    required
                  />
                </div>
                <div>
                  <label htmlFor="department" className="block text-sm font-medium text-gray-700 mb-2">
                    부서
                  </label>
                  <select
                    id="department"
                    name="department"
                    value={signupForm.department}
                    onChange={(e) => setSignupForm({...signupForm, department: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-black"
                    required
                  >
                    <option value="">부서를 선택하세요</option>
                    <option value="emergency">응급실</option>
                    <option value="internal">내과</option>
                    <option value="surgery">외과</option>
                    <option value="pediatrics">소아과</option>
                    <option value="obstetrics">산부인과</option>
                    <option value="radiology">영상의학과</option>
                    <option value="laboratory">검사실</option>
                    <option value="nursing">간호부</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                    비밀번호
                  </label>
                  <input
                    type="password"
                    id="password"
                    name="password"
                    value={signupForm.password}
                    onChange={(e) => setSignupForm({...signupForm, password: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-black placeholder-gray-500"
                    placeholder="••••••••"
                    required
                  />
                </div>
                <div>
                  <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                    비밀번호 확인
                  </label>
                  <input
                    type="password"
                    id="confirmPassword"
                    name="confirmPassword"
                    value={signupForm.confirmPassword}
                    onChange={(e) => setSignupForm({...signupForm, confirmPassword: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-black placeholder-gray-500"
                    placeholder="••••••••"
                    required
                  />
                </div>
                <div className="flex items-center">
                  <input
                    id="agree-terms"
                    name="agree-terms"
                    type="checkbox"
                    checked={signupForm.agreeTerms}
                    onChange={(e) => setSignupForm({...signupForm, agreeTerms: e.target.checked})}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    required
                  />
                  <label htmlFor="agree-terms" className="ml-2 block text-sm text-gray-900">
                    <a href="#" className="text-indigo-600 hover:text-indigo-500">이용약관</a>과{' '}
                    <a href="#" className="text-indigo-600 hover:text-indigo-500">개인정보처리방침</a>에 동의합니다
                  </label>
                </div>
                <div>
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? '회원가입 중...' : '회원가입'}
                  </button>
                </div>
                
                {/* 메시지 표시 */}
                {message && (
                  <div className={`mt-4 p-3 rounded-md text-sm ${
                    message.includes('성공') || message.includes('완료') 
                      ? 'bg-green-100 text-green-700 border border-green-200' 
                      : 'bg-red-100 text-red-700 border border-red-200'
                  }`}>
                    {message}
                  </div>
                )}
              </form>
            </div>
          )}

          {activeTab === 'location' && (
            <div className="max-w-4xl mx-auto">
              <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">병실 위치 가이드</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[101, 102, 103, 201, 202, 203, 301, 302, 303].map((room) => (
                  <div key={room} className="bg-gray-50 rounded-lg p-6 border border-gray-200 hover:shadow-md transition-shadow">
                    <div className="text-center">
                      <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <span className="text-2xl font-bold text-indigo-600">{room}</span>
                      </div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-2">{room}실</h4>
                      <p className="text-sm text-gray-600 mb-4">
                        {room < 200 ? '1층' : room < 300 ? '2층' : '3층'}
                      </p>
                      <button
                        onClick={() => window.open(`/heal_base_hospital_worker/v1/web/ensure/logined/and/hospital-location-guided/${room}`, '_blank')}
                        className="w-full bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 transition-colors"
                      >
                        위치 확인
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>

      {/* 푸터 */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <div className="text-center text-gray-500 text-sm">
            <p>&copy; 2025 병원 근무자 관리 시스템. 모든 권리 보유.</p>
            <p className="mt-2">
              <a href="#" className="text-indigo-600 hover:text-indigo-500">개인정보처리방침</a>
              {' • '}
              <a href="#" className="text-indigo-600 hover:text-indigo-500">이용약관</a>
              {' • '}
              <a href="#" className="text-indigo-600 hover:text-indigo-500">고객지원</a>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
