from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

async def delete_financial_statements(
    db_session: AsyncSession,
    corp_code: str,
    rcept_no: str,
    year: Optional[int] = None
) -> None:
    """재무제표 데이터를 삭제합니다.
    
    Args:
        db_session: 데이터베이스 세션
        corp_code: 회사 코드
        rcept_no: 접수번호
        year: 삭제할 연도. None이면 모든 연도의 데이터 삭제
    """
    query = text("""
        DELETE FROM fin_data 
        WHERE corp_code = :corp_code 
        AND rcept_no = :rcept_no
    """)
    
    if year is not None:
        query = text("""
            DELETE FROM fin_data 
            WHERE corp_code = :corp_code 
            AND rcept_no = :rcept_no
            AND bsns_year = :year
        """)
        await db_session.execute(query, {"corp_code": corp_code, "rcept_no": rcept_no, "year": str(year)})
    else:
        await db_session.execute(query, {"corp_code": corp_code, "rcept_no": rcept_no})
    
    await db_session.commit()

async def insert_financial_statement(db_session: AsyncSession, data: Dict[str, Any]) -> None:
    """재무제표 데이터를 저장합니다."""
    query = text("""
        INSERT INTO fin_data (
            corp_code, corp_name, stock_code, bsns_year, sj_div, sj_nm, 
            account_nm, thstrm_amount, frmtrm_amount, bfefrmtrm_amount, ord
        ) VALUES (
            :corp_code, :corp_name, :stock_code, :bsns_year, :sj_div, :sj_nm,
            :account_nm, :thstrm_amount, :frmtrm_amount, :bfefrmtrm_amount, :ord
        )
    """)
    await db_session.execute(query, data)
    await db_session.commit()

async def get_statement_summary(db_session: AsyncSession) -> List[Dict[str, Any]]:
    """회사별 재무제표 종류와 데이터 수를 조회합니다."""
    query = text("""
        SELECT corp_code, corp_name, sj_div, sj_nm, COUNT(*) as count
        FROM fin_data
        GROUP BY corp_code, corp_name, sj_div, sj_nm
        ORDER BY corp_code, sj_div
    """)
    result = await db_session.execute(query)
    return [dict(row) for row in result]

async def get_key_financial_items(db_session: AsyncSession) -> List[Dict[str, Any]]:
    """주요 재무 항목을 조회합니다."""
    query = text("""
        SELECT 
            corp_code, corp_name, bsns_year, sj_div, sj_nm,
            account_nm, thstrm_amount, frmtrm_amount, bfefrmtrm_amount
        FROM fin_data
        WHERE account_nm IN (
            '자산총계', '부채총계', '자본총계', '유동자산', '유동부채',
            '매출액', '영업이익', '당기순이익', '영업활동현금흐름'
        )
        ORDER BY corp_code, bsns_year DESC, sj_div, account_nm
    """)
    result = await db_session.execute(query)
    return [dict(row) for row in result]

async def get_company_by_name(db_session: AsyncSession, company_name: str) -> Optional[Dict[str, Any]]:
    """회사명으로 회사 정보를 조회합니다."""
    query = text("""
        SELECT DISTINCT corp_code, corp_name, stock_code
        FROM fin_data
        WHERE corp_name = :company_name
        LIMIT 1
    """)
    result = await db_session.execute(query, {"company_name": company_name})
    row = result.fetchone()
    if row:
        if isinstance(row, dict):
            return row
        return dict(zip(result.keys(), row))
    return None

async def get_financial_statements_by_corp_code(db_session: AsyncSession, corp_code: str) -> List[Dict[str, Any]]:
    """회사 코드로 재무제표 데이터를 조회합니다."""
    query = text("""
        SELECT 
            corp_code, corp_name, stock_code, rcept_no, reprt_code,
            bsns_year, sj_div, sj_nm, account_nm, thstrm_nm,
            thstrm_amount, frmtrm_nm, frmtrm_amount, bfefrmtrm_nm,
            bfefrmtrm_amount, ord, currency
        FROM fin_data
        WHERE corp_code = :corp_code
        ORDER BY bsns_year DESC, sj_div, ord
    """)
    result = await db_session.execute(query, {"corp_code": corp_code})
    return [dict(row) for row in result]

async def save_financial_statements(db_session: AsyncSession, statements: List[Dict[str, Any]]) -> None:
    """재무제표 데이터를 저장합니다."""
    try:
        for statement in statements:
            await insert_financial_statement(db_session, statement)
    except Exception as e:
        logger.error(f"Error saving financial statements: {e}")
        raise

async def save_financial_ratios(db_session: AsyncSession, ratios: Dict[str, Any]) -> None:
    """재무비율을 저장합니다."""
    query = text("""
        INSERT INTO fin_data (
            corp_code, corp_name, bsns_year,
            debt_ratio, current_ratio, interest_coverage_ratio,
            operating_profit_ratio, net_profit_ratio, roe, roa,
            debt_dependency, cash_flow_debt_ratio,
            sales_growth, operating_profit_growth, eps_growth
        ) VALUES (
            :corp_code, :corp_name, :bsns_year,
            :debt_ratio, :current_ratio, :interest_coverage_ratio,
            :operating_profit_ratio, :net_profit_ratio, :roe, :roa,
            :debt_dependency, :cash_flow_debt_ratio,
            :sales_growth, :operating_profit_growth, :eps_growth
        )
        ON CONFLICT (corp_code, bsns_year) 
        DO UPDATE SET
            debt_ratio = EXCLUDED.debt_ratio,
            current_ratio = EXCLUDED.current_ratio,
            interest_coverage_ratio = EXCLUDED.interest_coverage_ratio,
            operating_profit_ratio = EXCLUDED.operating_profit_ratio,
            net_profit_ratio = EXCLUDED.net_profit_ratio,
            roe = EXCLUDED.roe,
            roa = EXCLUDED.roa,
            debt_dependency = EXCLUDED.debt_dependency,
            cash_flow_debt_ratio = EXCLUDED.cash_flow_debt_ratio,
            sales_growth = EXCLUDED.sales_growth,
            operating_profit_growth = EXCLUDED.operating_profit_growth,
            eps_growth = EXCLUDED.eps_growth
    """)
    await db_session.execute(query, ratios)
    await db_session.commit()

async def get_financial_statements(db_session: AsyncSession, corp_code: str, bsns_year: str) -> List[Dict[str, Any]]:
    """회사 코드와 사업연도로 재무제표 데이터를 조회합니다."""
    query = text("""
        SELECT 
            corp_code,
            corp_name,
            stock_code,
            rcept_no,
            reprt_code,
            bsns_year,
            sj_div,
            sj_nm,
            account_nm,
            thstrm_nm,
            thstrm_amount,
            frmtrm_nm,
            frmtrm_amount,
            bfefrmtrm_nm,
            bfefrmtrm_amount,
            ord,
            currency
        FROM fin_data
        WHERE corp_code = :corp_code
        AND bsns_year = :bsns_year
        ORDER BY sj_div, ord
    """)
    result = await db_session.execute(query, {"corp_code": corp_code, "bsns_year": bsns_year})
    rows = result.fetchall()
    return [dict(zip(result.keys(), row)) for row in rows]