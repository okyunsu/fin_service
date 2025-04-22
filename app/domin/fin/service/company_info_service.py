from typing import Dict, Any
import logging
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domin.fin.models.schemas import CompanyInfo
from app.domin.fin.service.dart_api_service import DartApiService

logger = logging.getLogger(__name__)

class CompanyInfoService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.dart_api = DartApiService()

    async def get_company_info(self, company_name: str) -> CompanyInfo:
        """회사 정보를 조회합니다."""
        try:
            # DB에서 먼저 조회
            db_company = await self._get_company_from_db(company_name)
            if db_company:
                # 딕셔너리 키를 CompanyInfo 필드와 일치시킴
                company_data = {
                    "corp_code": db_company.get("corp_code", ""),
                    "corp_name": db_company.get("corp_name", company_name),
                    "stock_code": db_company.get("stock_code", ""),
                    "modify_date": datetime.now().strftime("%Y%m%d")
                }
                try:
                    return CompanyInfo(**company_data)
                except Exception as e:
                    logger.warning(f"DB 데이터로 CompanyInfo 생성 실패: {e}")
            
            # API에서 조회
            return await self.dart_api.fetch_company_info(company_name)
            
        except Exception as e:
            logger.error(f"회사 정보 조회 실패: {str(e)}")
            raise

    async def _get_company_from_db(self, company_name: str) -> Dict[str, Any]:
        """DB에서 회사 정보를 조회합니다."""
        query = text("""
            SELECT corp_code, corp_name, stock_code 
            FROM fin_data 
            WHERE corp_name = :company_name 
            LIMIT 1
        """)
        result = await self.db_session.execute(query, {"company_name": company_name})
        row = result.fetchone()
        
        if row:
            return {
                "corp_code": row[0],
                "corp_name": row[1],
                "stock_code": row[2]
            }
        return None 