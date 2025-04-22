from typing import Dict, Any, List, Optional
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domin.fin.models.schemas import RawFinancialStatement, CompanyInfo
from app.domin.fin.repository.fin_repository import (
    delete_financial_statements,
    save_financial_statements
)
from app.domin.fin.service.dart_api_service import DartApiService
from app.domin.fin.service.financial_data_processor import FinancialDataProcessor
from app.domin.fin.service.ratio_service import RatioService
from app.domin.fin.service.company_info_service import CompanyInfoService

logger = logging.getLogger(__name__)

class FinancialStatementService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.dart_api = DartApiService()
        self.data_processor = FinancialDataProcessor()
        self.ratio_service = RatioService(db_session)
        self.company_info_service = CompanyInfoService(db_session)

    async def get_financial_statements(self, company_info: CompanyInfo, year: Optional[int] = None) -> List[RawFinancialStatement]:
        """재무제표 데이터를 조회합니다.
        
        Args:
            company_info: 회사 정보
            year: 조회할 연도. None이면 직전 연도의 데이터를 조회
        """
        try:
            statements = await self.dart_api.fetch_financial_statements(company_info.corp_code, year)
            logger.info(f"조회된 재무제표 수: {len(statements)}")
            return statements
        except Exception as e:
            logger.error(f"재무제표 조회 실패: {str(e)}")
            raise

    async def fetch_and_save_financial_data(self, company_name: str, year: Optional[int] = None) -> Dict[str, Any]:
        """회사명으로 재무제표 데이터를 조회하고 저장합니다.
        
        Args:
            company_name: 회사명
            year: 조회할 연도. None이면 직전 연도의 데이터를 조회
        """
        try:
            # 1. 회사 정보 조회
            company_info = await self.company_info_service.get_company_info(company_name)
            
            # 2. 기존 데이터 확인
            if year is not None:
                check_query = text("""
                    SELECT bsns_year, sj_div, sj_nm, account_nm, 
                           thstrm_amount, frmtrm_amount, bfefrmtrm_amount
                    FROM fin_data 
                    WHERE corp_name = :company_name
                    AND bsns_year = :year
                    AND sj_div != 'RATIO'
                    ORDER BY bsns_year DESC, sj_div, ord
                """)
                result = await self.db_session.execute(check_query, {
                    "company_name": company_name,
                    "year": str(year)
                })
            else:
                check_query = text("""
                    SELECT bsns_year, sj_div, sj_nm, account_nm, 
                           thstrm_amount, frmtrm_amount, bfefrmtrm_amount
                    FROM fin_data 
                    WHERE corp_name = :company_name
                    AND sj_div != 'RATIO'
                    ORDER BY bsns_year DESC, sj_div, ord
                """)
                result = await self.db_session.execute(check_query, {
                    "company_name": company_name
                })
            
            # 결과를 딕셔너리로 변환
            data = []
            for row in result:
                row_dict = {}
                for idx, column in enumerate(result.keys()):
                    row_dict[column] = row[idx]
                data.append(row_dict)
            
            # 기존 데이터가 있으면 반환
            if data:
                logger.info(f"기존 데이터가 존재합니다: {company_name}, 연도: {year}")
                return {
                    "status": "success",
                    "message": f"{company_name}의 재무제표 데이터가 이미 존재합니다.",
                    "data": data
                }
            
            # 3. 재무제표 데이터 조회
            statements = await self.get_financial_statements(company_info, year)
            
            if not statements:
                return {
                    "status": "error",
                    "message": "재무제표 데이터를 찾을 수 없습니다."
                }
            
            # 4. 중복 제거
            statements = self.data_processor.deduplicate_statements(statements)
            
            # 5. 새로운 데이터 저장
            statement_data = [self.data_processor.prepare_statement_data(stmt, company_info) for stmt in statements]
            await save_financial_statements(self.db_session, statement_data)
            
            # 6. 재무비율 계산 및 저장 (한 번만 실행)
            bsns_year = statements[0].bsns_year if statements else None
            if bsns_year:
                # 기존 재무비율 데이터 확인
                ratio_check_query = text("""
                    SELECT 1 FROM fin_data 
                    WHERE corp_code = :corp_code 
                    AND bsns_year = :bsns_year
                    AND sj_div = 'RATIO'
                    LIMIT 1
                """)
                ratio_result = await self.db_session.execute(ratio_check_query, {
                    "corp_code": company_info.corp_code,
                    "bsns_year": bsns_year
                })
                
                # 재무비율 데이터가 없을 때만 계산 및 저장
                if not ratio_result.fetchone():
                    ratios = await self.ratio_service.calculate_and_save_ratios(
                        corp_code=company_info.corp_code,
                        corp_name=company_info.corp_name,
                        bsns_year=bsns_year
                    )
            
            # 7. 저장된 데이터 조회하여 반환
            if year is not None:
                data_query = text("""
                    SELECT bsns_year, sj_div, sj_nm, account_nm, 
                           thstrm_amount, frmtrm_amount, bfefrmtrm_amount
                    FROM fin_data 
                    WHERE corp_name = :company_name
                    AND bsns_year = :year
                    AND sj_div != 'RATIO'
                    ORDER BY bsns_year DESC, sj_div, ord
                """)
                data_result = await self.db_session.execute(data_query, {
                    "company_name": company_name,
                    "year": str(year)
                })
            else:
                data_query = text("""
                    SELECT bsns_year, sj_div, sj_nm, account_nm, 
                           thstrm_amount, frmtrm_amount, bfefrmtrm_amount
                    FROM fin_data 
                    WHERE corp_name = :company_name
                    AND sj_div != 'RATIO'
                    ORDER BY bsns_year DESC, sj_div, ord
                """)
                data_result = await self.db_session.execute(data_query, {
                    "company_name": company_name
                })
            
            # 결과를 딕셔너리로 변환
            data = []
            for row in data_result:
                row_dict = {}
                for idx, column in enumerate(data_result.keys()):
                    row_dict[column] = row[idx]
                data.append(row_dict)
            
            return {
                "status": "success",
                "message": f"{company_name}의 재무제표 데이터가 성공적으로 저장되었습니다.",
                "data": data
            }
            
        except Exception as e:
            logger.error(f"재무제표 데이터 저장 실패: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            } 