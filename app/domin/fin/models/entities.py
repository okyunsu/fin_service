from sqlalchemy import Column, Integer, String, DateTime, JSON
from app.foundation.infra.database.base import Base
from datetime import datetime

class FinancialStatement(Base):
    __tablename__ = "fin_statements"

    id = Column(Integer, primary_key=True, index=True)
    rcept_no = Column(String)                    # 접수번호
    reprt_code = Column(String)                  # 보고서 코드
    bsns_year = Column(String)                   # 사업연도
    corp_code = Column(String)                   # 회사 코드
    sj_div = Column(String)                      # 재무제표 구분    
    sj_nm = Column(String)                       # 재무제표명
    account_nm = Column(String)                  # 계정명
    thstrm_nm = Column(String)                   # 당기명
    thstrm_amount = Column(String)               # 당기금액
    frmtrm_nm = Column(String)                   # 전기명
    frmtrm_amount = Column(String)               # 전기금액
    bfefrmtrm_nm = Column(String)               # 전전기명
    bfefrmtrm_amount = Column(String)           # 전전기금액
    ord = Column(String)                        # 계정과목 정렬순서
    currency = Column(String)                   # 통화 단위
    crawling_date = Column(DateTime, default=datetime.utcnow)
    data_source = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)