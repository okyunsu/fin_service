from typing import List, Dict, Any, Optional
import logging
from app.domin.fin.models.schemas import RawFinancialStatement, CompanyInfo

logger = logging.getLogger(__name__)

class FinancialDataProcessor:
    def __init__(self):
        pass

    def convert_amount(self, amount_str: Optional[str]) -> float:
        """금액 문자열을 숫자로 변환합니다."""
        if not amount_str:
            return 0.0
        try:
            return float(amount_str.replace(",", ""))
        except (ValueError, AttributeError) as e:
            logger.warning(f"금액 변환 실패: {amount_str}, 에러: {str(e)}")
            return 0.0

    def deduplicate_statements(self, statements: List[RawFinancialStatement]) -> List[RawFinancialStatement]:
        """중복되는 계정과목을 제거하고 가장 최신의 금액만 남깁니다."""
        latest_statements = {}
        for stmt in statements:
            key = (stmt.account_nm, stmt.sj_nm)
            if key not in latest_statements or int(stmt.ord) < int(latest_statements[key].ord):
                latest_statements[key] = stmt
        return list(latest_statements.values())

    def prepare_statement_data(self, statement: RawFinancialStatement, company_info: CompanyInfo) -> Dict[str, Any]:
        """재무제표 데이터를 DB 저장 형식으로 변환합니다."""
        return {
            "corp_code": company_info.corp_code,
            "corp_name": company_info.corp_name,
            "stock_code": company_info.stock_code,
            "rcept_no": statement.rcept_no,
            "reprt_code": statement.reprt_code,
            "bsns_year": statement.bsns_year,
            "sj_div": statement.sj_div,
            "sj_nm": statement.sj_nm,
            "account_nm": statement.account_nm,
            "thstrm_nm": statement.thstrm_nm,
            "thstrm_amount": self.convert_amount(statement.thstrm_amount),
            "frmtrm_nm": statement.frmtrm_nm,
            "frmtrm_amount": self.convert_amount(statement.frmtrm_amount),
            "bfefrmtrm_nm": statement.bfefrmtrm_nm,
            "bfefrmtrm_amount": self.convert_amount(statement.bfefrmtrm_amount),
            "ord": statement.ord,
            "currency": statement.currency
        } 