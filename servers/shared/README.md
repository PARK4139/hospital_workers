# Shared Modules

## 📦 공통 모듈 구조

### 데이터베이스 모델
- `models/` - SQLAlchemy 모델
- `database.py` - 데이터베이스 연결 설정

### 유틸리티
- `utils/` - 공통 유틸리티 함수
- `config.py` - 설정 관리
- `exceptions.py` - 커스텀 예외

### DDD 도메인
- `domain/` - 도메인 엔티티와 서비스
- `repositories/` - 리포지토리 패턴

## 🔗 사용법

각 서비스에서 공통 모듈을 import하여 사용:

```python
from shared.models import User
from shared.database import get_db
from shared.utils import ensure_valid_token
```
