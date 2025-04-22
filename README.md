# Financial Service API

FastAPI 기반의 금융 서비스 API 프로젝트입니다.

## 기술 스택

- **Backend Framework**: FastAPI 0.110.0
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0.27
- **Migration**: Alembic 1.13.1
- **Container**: Docker & Docker Compose

## 주요 기능

- FastAPI를 사용한 RESTful API 구현
- PostgreSQL 데이터베이스 연동
- Docker를 통한 컨테이너화
- 환경 변수를 통한 설정 관리

## 시작하기

### 필수 조건

- Docker
- Docker Compose
- Python 3.8 이상

### 환경 설정

1. 프로젝트 클론
```bash
git clone [repository-url]
cd fin_service
```

2. 환경 변수 설정
```bash
# .env 파일 생성
cp .env.example .env
# .env 파일을 편집하여 필요한 환경 변수 설정
```

### 실행 방법

1. Docker Compose로 서비스 실행
```bash
docker-compose up -d
```

2. API 서버 접속
- API 서버: http://localhost:8000
- API 문서: http://localhost:8000/docs

## 프로젝트 구조

```
fin_service/
├── app/                    # 애플리케이션 소스 코드
├── .env                    # 개발 환경 변수
├── .env.production         # 프로덕션 환경 변수
├── docker-compose.yml      # Docker Compose 설정
├── Dockerfile             # Docker 이미지 설정
├── requirements.txt       # Python 패키지 의존성
└── .sql                   # SQL 스크립트
```

## 환경 변수

필요한 환경 변수는 `.env` 파일에서 설정할 수 있습니다. 주요 환경 변수는 다음과 같습니다:

- `DATABASE_URL`: PostgreSQL 데이터베이스 연결 문자열
- `API_KEY`: API 인증 키
- 기타 필요한 환경 변수들...

## 라이선스

이 프로젝트는 [라이선스 정보] 하에 배포됩니다. 