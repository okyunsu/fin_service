from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from typing import Callable
from fastapi.responses import HTMLResponse
import logging
import os
from dotenv import load_dotenv

from app.api.fin.fin_router import router as fin_router
from app.foundation.infra.database.database import init_db

# 환경 변수 로드
env = os.getenv("APP_ENV", "development")
if env == "development":
    load_dotenv(".env")
else:
    # 프로덕션 환경에서는 Railway의 환경 변수를 사용
    load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(fin_router, tags=["financial"])

current_time: Callable[[], str] = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting application in {env} environment")
    await init_db()
    logger.info("Database initialized")

@app.get("/")
async def home():
    logger.info("Accessing home page")
    try:
        content = f"""
<body>
<div style="width: 400px; margin: 50 auto;">
    <h1>emart 크롤러 API</h1>
    <p>Welcome to the emart Crawler API</p>
    <p>Current time (UTC): {current_time()}</p>
    <p>Environment: {env}</p>
</div>
</body>
"""
        return HTMLResponse(content=content)
    except Exception as e:
        logger.error(f"Error in home page: {str(e)}")
        raise 