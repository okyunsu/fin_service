from fastapi import HTTPException, Query
from app.domin.fin.service.fin_service import FinService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging
from typing import Optional

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FinController:
    def __init__(self, db_session: AsyncSession):
        logger.info("FinController가 초기화되었습니다.")
        self.db_session = db_session
        self.service = FinService(db_session)

    async def get_financial(
        self, 
        company_name: str = Query(..., description="회사명"),
        year: Optional[int] = Query(None, description="조회할 연도. 지정하지 않으면 직전 연도의 데이터를 조회")
    ):
        """재무제표 데이터를 조회합니다.
        
        Args:
            company_name: 회사명
            year: 조회할 연도. None이면 직전 연도의 데이터를 조회
        """
        logger.info(f"재무제표 조회 요청 - 회사: {company_name}, 연도: {year}")
        try:
            data = await self.service.fetch_and_save_financial_data(
                company_name=company_name,
                year=year
            )
            logger.info(f"재무제표 조회 성공 - 회사: {company_name}, 연도: {year}")
            return {
                "status": "success", 
                "message": "재무정보가 성공적으로 조회되었습니다.",
                "data": data
            }
        except ValueError as e:
            # 회사명 관련 오류
            error_message = str(e)
            logger.error(f"회사명 관련 오류: {error_message}")
            raise HTTPException(status_code=400, detail=error_message)
        except Exception as e:
            # 기타 오류
            error_message = str(e)
            logger.error(f"기타 오류: {error_message}")
            raise HTTPException(status_code=500, detail=error_message)

    async def get_financial_ratios(
        self, 
        company_name: str = Query(..., description="회사명"),
        year: Optional[int] = Query(None, description="조회할 연도. 지정하지 않으면 직전 연도의 데이터를 조회")
    ):
        """회사명으로 재무비율을 조회합니다.
        
        Args:
            company_name: 회사명
            year: 조회할 연도. None이면 직전 연도의 데이터를 조회
        """
        logger.info(f"재무비율 조회 요청 - 회사: {company_name}, 연도: {year}")
        try:
            # 회사 코드 조회 (fin_data 테이블에서)
            company_query = text("""
                SELECT DISTINCT corp_code FROM fin_data WHERE corp_name = :company_name
            """)
            company_result = await self.db_session.execute(company_query, {"company_name": company_name})
            company_row = company_result.fetchone()
            
            if not company_row:
                logger.warning(f"회사명 '{company_name}'에 해당하는 회사 코드를 찾을 수 없습니다.")
                # 회사 정보가 없으면 DART API에서 데이터를 가져옴
                data = await self.service.fetch_and_save_financial_data(
                    company_name=company_name,
                    year=year
                )
                if data["status"] == "error":
                    logger.warning(f"재무제표 데이터 조회 실패 - 회사: {company_name}")
                    return {
                        "status": "success",
                        "message": "재무비율이 성공적으로 조회되었습니다.",
                        "data": []
                    }
                # 데이터를 가져온 후 다시 회사 코드 조회
                company_result = await self.db_session.execute(company_query, {"company_name": company_name})
                company_row = company_result.fetchone()
                if not company_row:
                    logger.warning(f"회사 코드를 찾을 수 없습니다 - 회사: {company_name}")
                    return {
                        "status": "success",
                        "message": "재무비율이 성공적으로 조회되었습니다.",
                        "data": []
                    }
            
            corp_code = company_row[0]
            logger.info(f"회사 코드: {corp_code}")
            
            # 재무비율 데이터 가져오기 (한글 필드명 사용)
            ratios_query = text("""
                SELECT 
                    bsns_year as "사업연도",
                    ROUND(debt_ratio, 2) as "부채비율",
                    ROUND(current_ratio, 2) as "유동비율",
                    ROUND(interest_coverage_ratio, 2) as "이자보상배율",
                    ROUND(operating_profit_ratio, 2) as "영업이익률",
                    ROUND(net_profit_ratio, 2) as "순이익률",
                    ROUND(roe, 2) as "ROE",
                    ROUND(roa, 2) as "ROA",
                    ROUND(debt_dependency, 2) as "부채의존도",
                    ROUND(cash_flow_debt_ratio, 2) as "현금흐름부채비율",
                    ROUND(sales_growth, 2) as "매출액증가율",
                    ROUND(operating_profit_growth, 2) as "영업이익증가율",
                    ROUND(eps_growth, 2) as "EPS증가율"
                FROM fin_data 
                WHERE corp_code = :corp_code
                AND (
                    debt_ratio IS NOT NULL OR
                    current_ratio IS NOT NULL OR
                    interest_coverage_ratio IS NOT NULL OR
                    operating_profit_ratio IS NOT NULL OR
                    net_profit_ratio IS NOT NULL OR
                    roe IS NOT NULL OR
                    roa IS NOT NULL OR
                    debt_dependency IS NOT NULL OR
                    cash_flow_debt_ratio IS NOT NULL OR
                    sales_growth IS NOT NULL OR
                    operating_profit_growth IS NOT NULL OR
                    eps_growth IS NOT NULL
                )
            """)
            
            if year is not None:
                ratios_query = text(str(ratios_query) + " AND bsns_year = :year")
                ratios_result = await self.db_session.execute(ratios_query, {"corp_code": corp_code, "year": str(year)})
                
                # 해당 연도의 데이터가 없으면 DART API에서 가져옴
                if ratios_result.rowcount == 0:
                    logger.info(f"해당 연도({year})의 데이터가 없어 DART API에서 가져옵니다.")
                    data = await self.service.fetch_and_save_financial_data(
                        company_name=company_name,
                        year=year
                    )
                    if data["status"] == "success":
                        # 데이터를 가져온 후 다시 조회
                        ratios_result = await self.db_session.execute(ratios_query, {"corp_code": corp_code, "year": str(year)})
            else:
                # 연도가 지정되지 않았으면 최신 연도의 데이터만 조회
                ratios_query = text(str(ratios_query) + " AND bsns_year = (SELECT MAX(bsns_year) FROM fin_data WHERE corp_code = :corp_code)")
                ratios_result = await self.db_session.execute(ratios_query, {"corp_code": corp_code})
            
            # 결과를 딕셔너리로 변환
            ratios = []
            for row in ratios_result:
                ratio_dict = {
                    "사업연도": row[0],
                    "부채비율": row[1],
                    "유동비율": row[2],
                    "이자보상배율": row[3],
                    "영업이익률": row[4],
                    "순이익률": row[5],
                    "ROE": row[6],
                    "ROA": row[7],
                    "부채의존도": row[8],
                    "현금흐름부채비율": row[9],
                    "매출액증가율": row[10],
                    "영업이익증가율": row[11],
                    "EPS증가율": row[12]
                }
                # null이 아닌 값만 포함
                ratio_dict = {k: v for k, v in ratio_dict.items() if v is not None}
                ratios.append(ratio_dict)
                
            logger.info(f"조회된 재무비율 수: {len(ratios)}")
            
            return {
                "status": "success",
                "message": "재무비율이 성공적으로 조회되었습니다.",
                "data": ratios
            }
        except ValueError as e:
            # 회사명 관련 오류
            error_message = str(e)
            logger.error(f"회사명 관련 오류: {error_message}")
            raise HTTPException(status_code=400, detail=error_message)
        except Exception as e:
            # 기타 오류
            error_message = str(e)
            logger.error(f"기타 오류: {error_message}")
            raise HTTPException(status_code=500, detail=error_message)