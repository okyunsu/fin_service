from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from datetime import datetime
from sqlalchemy import text

logger = logging.getLogger(__name__)

class RatioService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    def _calculate_growth_rate(self, current: float, previous: float) -> float:
        """성장률을 계산합니다."""
        if previous == 0:
            return 0.0
        return ((current - previous) / abs(previous)) * 100

    async def _get_financial_statements(self, corp_code: str, bsns_year: str) -> List[Dict[str, Any]]:
        """재무제표 데이터를 조회합니다."""
        query = text("""
            SELECT * FROM fin_data 
            WHERE corp_code = :corp_code 
            AND bsns_year = :bsns_year
            AND sj_div IN ('BS', 'IS')
            ORDER BY sj_div, ord
        """)
        result = await self.db_session.execute(query, {
            "corp_code": corp_code,
            "bsns_year": bsns_year
        })
        
        statements = []
        for row in result:
            row_dict = {}
            for idx, column in enumerate(result.keys()):
                row_dict[column] = row[idx]
            statements.append(row_dict)
        
        return statements

    def _extract_financial_data(self, statements: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """재무제표 데이터에서 필요한 항목을 추출합니다."""
        financial_data = {
            "BS": {},  # 재무상태표
            "IS": {}   # 손익계산서
        }
        
        for statement in statements:
            sj_div = statement["sj_div"]
            account_nm = statement["account_nm"]
            
            # 당기, 전기, 전전기 데이터 추출
            financial_data[sj_div][account_nm] = {
                "current": float(statement["thstrm_amount"]),
                "previous": float(statement["frmtrm_amount"]),
                "prev_previous": float(statement["bfefrmtrm_amount"])
            }
        
        return financial_data

    def _calculate_ratios(self, financial_data: Dict[str, Dict[str, Dict[str, float]]]) -> Dict[str, float]:
        """재무비율을 계산합니다."""
        ratios = {}
        bs_data = financial_data["BS"]
        is_data = financial_data["IS"]
        
        # 안정성 지표
        if "자산총계" in bs_data and "부채총계" in bs_data and "자본총계" in bs_data:
            total_assets = bs_data["자산총계"]["current"]
            total_liabilities = bs_data["부채총계"]["current"]
            total_equity = bs_data["자본총계"]["current"]
            
            if total_equity > 0:
                ratios["debt_ratio"] = (total_liabilities / total_equity) * 100
            
            if total_assets > 0:
                ratios["roa"] = (is_data["당기순이익"]["current"] / total_assets) * 100
        
        if "유동자산" in bs_data and "유동부채" in bs_data:
            current_assets = bs_data["유동자산"]["current"]
            current_liabilities = bs_data["유동부채"]["current"]
            if current_liabilities > 0:
                ratios["current_ratio"] = (current_assets / current_liabilities) * 100
        
        # 수익성 지표
        if "매출액" in is_data and "영업이익" in is_data and "당기순이익" in is_data:
            revenue = is_data["매출액"]["current"]
            operating_profit = is_data["영업이익"]["current"]
            net_income = is_data["당기순이익"]["current"]
            
            if revenue > 0:
                ratios["operating_profit_ratio"] = (operating_profit / revenue) * 100
                ratios["net_profit_ratio"] = (net_income / revenue) * 100
            
            if "자본총계" in bs_data and bs_data["자본총계"]["current"] > 0:
                ratios["roe"] = (net_income / bs_data["자본총계"]["current"]) * 100
        
        # 성장률 지표
        if "매출액" in is_data:
            ratios["sales_growth"] = self._calculate_growth_rate(
                is_data["매출액"]["current"],
                is_data["매출액"]["previous"]
            )
        
        if "영업이익" in is_data:
            ratios["operating_profit_growth"] = self._calculate_growth_rate(
                is_data["영업이익"]["current"],
                is_data["영업이익"]["previous"]
            )
        
        return ratios

    async def calculate_financial_ratios(self, corp_code: str, bsns_year: str) -> Dict[str, Any]:
        """재무비율을 계산합니다."""
        try:
            statements = await self._get_financial_statements(corp_code, bsns_year)
            if not statements:
                logger.warning(f"재무제표 데이터가 없습니다: {corp_code}, {bsns_year}")
                return {}
            
            financial_data = self._extract_financial_data(statements)
            ratios = self._calculate_ratios(financial_data)
            
            return {
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                **ratios
            }
            
        except Exception as e:
            logger.error(f"재무비율 계산 중 오류 발생: {str(e)}")
            raise

    async def calculate_and_save_ratios(self, corp_code: str, corp_name: str, bsns_year: str) -> Dict[str, Any]:
        """재무비율을 계산하고 저장합니다."""
        try:
            ratios = await self.calculate_financial_ratios(corp_code, bsns_year)
            if not ratios:
                return {}
            
            await self._save_ratios(corp_code, corp_name, bsns_year, ratios)
            return ratios
            
        except Exception as e:
            logger.error(f"재무비율 계산 및 저장 실패: {str(e)}")
            raise

    async def _save_ratios(self, corp_code: str, corp_name: str, bsns_year: str, ratios: Dict[str, float]) -> None:
        """계산된 재무비율을 저장합니다."""
        try:
            # 기존 재무비율 데이터 삭제
            delete_query = text("""
                DELETE FROM fin_data 
                WHERE corp_code = :corp_code 
                AND bsns_year = :bsns_year
                AND sj_div = 'RATIO'
            """)
            await self.db_session.execute(delete_query, {
                "corp_code": corp_code,
                "bsns_year": bsns_year
            })
            
            # 새로운 재무비율 데이터 저장
            insert_query = text("""
                INSERT INTO fin_data (
                    corp_code, corp_name, bsns_year, sj_div, sj_nm,
                    debt_ratio, current_ratio,
                    operating_profit_ratio, net_profit_ratio, roe, roa,
                    sales_growth, operating_profit_growth
                ) VALUES (
                    :corp_code, :corp_name, :bsns_year, 'RATIO', '재무비율',
                    :debt_ratio, :current_ratio,
                    :operating_profit_ratio, :net_profit_ratio, :roe, :roa,
                    :sales_growth, :operating_profit_growth
                )
            """)
            
            # 기본값 설정
            ratio_data = {
                "corp_code": corp_code,
                "corp_name": corp_name,
                "bsns_year": bsns_year,
                **{k: ratios.get(k, 0) for k in [
                    "debt_ratio", "current_ratio",
                    "operating_profit_ratio", "net_profit_ratio", "roe", "roa",
                    "sales_growth", "operating_profit_growth"
                ]}
            }
            
            await self.db_session.execute(insert_query, ratio_data)
            await self.db_session.commit()
            
            logger.info(f"재무비율 저장 완료: {corp_code}, {bsns_year}")
            
        except Exception as e:
            logger.error(f"재무비율 저장 중 오류 발생: {str(e)}")
            await self.db_session.rollback()
            raise 