import os
import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

from app.domin.fin.service.company_info_service import CompanyInfoService
from app.domin.fin.service.financial_statement_service import FinancialStatementService
from app.domin.fin.models.schemas import CompanyInfo, RawFinancialStatement

# 로깅 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 핸들러가 없으면 추가
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

class FinService:
    def __init__(self, db_session: AsyncSession):
        """서비스 초기화"""
        logger.info("FinService가 초기화되었습니다.")
        self.db_session = db_session
        self.company_info_service = CompanyInfoService(db_session)
        self.financial_statement_service = FinancialStatementService(db_session)
        load_dotenv()
        self.api_key = os.getenv("DART_API_KEY")
        if not self.api_key:
            logger.error("DART API 키가 필요합니다.")
            raise ValueError("DART API 키가 필요합니다.")

    async def get_company_info(self, company_name: str) -> CompanyInfo:
        """회사 정보를 조회합니다."""
        logger.info(f"회사 정보 조회 시작: {company_name}")
        return await self.company_info_service.get_company_info(company_name)

    async def get_financial_statements(self, company_info: CompanyInfo, year: Optional[int] = None) -> list[RawFinancialStatement]:
        """재무제표 데이터를 조회합니다.
        
        Args:
            company_info: 회사 정보
            year: 조회할 연도. None이면 최신 연도의 데이터를 조회
        """
        logger.info(f"재무제표 조회 시작 - 회사: {company_info.corp_name}, 연도: {year}")
        return await self.financial_statement_service.get_financial_statements(company_info, year)

    async def fetch_and_save_financial_data(self, company_name: str, year: Optional[int] = None) -> Dict[str, Any]:
        """회사명으로 재무제표 데이터를 조회하고 저장합니다.
        
        Args:
            company_name: 회사명
            year: 조회할 연도. None이면 최신 연도의 데이터를 조회
        """
        logger.info(f"재무제표 데이터 조회 및 저장 시작 - 회사: {company_name}, 연도: {year}")
        return await self.financial_statement_service.fetch_and_save_financial_data(company_name, year)

