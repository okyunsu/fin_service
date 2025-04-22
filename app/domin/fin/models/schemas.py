from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# DART API 원본 데이터 스키마
class DartApiResponse(BaseModel):
    """DART API 응답 기본 구조"""
    status: str
    message: str
    list: Optional[List[dict]] = None

class AccountsForRatios(BaseModel):
    """재무비율 계산에 필요한 계정과목 데이터"""
    # 안정성 지표 계산용 계정
    total_liabilities: Optional[str] = None    # 부채총계 (부채비율)
    total_equity: Optional[str] = None         # 자본총계 (부채비율)
    current_assets: Optional[str] = None       # 유동자산 (유동비율)
    current_liabilities: Optional[str] = None  # 유동부채 (유동비율)
    operating_income: Optional[str] = None     # 영업이익 (이자보상배율)
    interest_expense: Optional[str] = None     # 이자비용 (이자보상배율)

    # 수익성 지표 계산용 계정
    net_income: Optional[str] = None          # 당기순이익 (ROE, ROA)
    total_assets: Optional[str] = None        # 자산총계 (ROA)

    # 건전성 지표 계산용 계정
    borrowings: Optional[str] = None          # 차입금 (차입금의존도)
    operating_cash_flow: Optional[str] = None # 영업활동현금흐름 (현금흐름대부채비율)

    # 성장성 지표 계산용 계정
    revenue: Optional[str] = None             # 당기 매출액 (매출 성장률)
    prev_revenue: Optional[str] = None        # 전기 매출액
    prev_operating_income: Optional[str] = None # 전기 영업이익 (영업이익 성장률)
    eps: Optional[str] = None                 # 당기 EPS (EPS 성장률)
    prev_eps: Optional[str] = None            # 전기 EPS

class RawFinancialStatement(BaseModel):
    """DART API 재무제표 원본 데이터"""
    rcept_no: str                    # 접수번호
    reprt_code: str                  # 보고서 코드
    bsns_year: str                   # 사업연도
    corp_code: str                   # 회사 코드
    sj_div: str                      # 재무제표 구분    
    sj_nm: str                       # 재무제표명
    account_nm: str                  # 계정명
    thstrm_nm: str                   # 당기명
    thstrm_amount: str               # 당기금액
    frmtrm_nm: str                   # 전기명
    frmtrm_amount: str               # 전기금액
    bfefrmtrm_nm: str               # 전전기명
    bfefrmtrm_amount: Optional[str] = None  # 전전기금액
    ord: int                        # 계정과목 정렬순서
    currency: str                   # 통화 단위

class CompanyInfo(BaseModel):
    """DART에서 제공하는 회사 기본 정보"""
    corp_code: str          # 회사 코드
    corp_name: str         # 회사명
    stock_code: str        # 주식 코드
    modify_date: str       # 최종 수정일 

class StockInfo(BaseModel):
    """주식 발행정보"""
    istc_totqy: int        # 발행한 주식의 총수
    distb_stock_qy: int    # 유통주식수
    tesstk_co: int         # 자기주식수 

class CompanyNameRequest(BaseModel):
    company_name: str

class FinancialMetrics(BaseModel):
    operatingMargin: List[float]
    netMargin: List[float]
    roe: List[float]
    roa: List[float]
    years: List[str]

class GrowthData(BaseModel):
    revenueGrowth: List[float]
    netIncomeGrowth: List[float]
    years: List[str]

class DebtLiquidityData(BaseModel):
    debtRatio: List[float]
    currentRatio: List[float]
    years: List[str]

class FinancialMetricsResponse(BaseModel):
    companyName: str
    financialMetrics: FinancialMetrics
    growthData: GrowthData
    debtLiquidityData: DebtLiquidityData
