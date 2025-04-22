from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

# 환경 변수 로드
env = os.getenv("APP_ENV", "development")
if env == "development":
    load_dotenv(".env")
else:
    # 프로덕션 환경에서는 Railway의 환경 변수를 사용
    load_dotenv()

# 데이터베이스 URL 설정
DATABASE_URL = os.getenv("DATABASE_URL")

# 비동기 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=True)

# 비동기 세션 팩토리 생성
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base 클래스 생성
Base = declarative_base()

async def get_db_session() -> AsyncSession:
    """데이터베이스 세션을 반환합니다."""
    session = async_session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

async def init_db():
    """데이터베이스 초기화 함수"""
    async with engine.begin() as conn:
        # 기존 테이블 삭제
        await conn.run_sync(Base.metadata.drop_all)
        # 테이블 생성
        await conn.run_sync(Base.metadata.create_all) 