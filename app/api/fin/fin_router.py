from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.domin.fin.controller.fin_controller import FinController
from app.foundation.infra.database.database import get_db_session
from app.domin.fin.models.schemas import (
    CompanyNameRequest,
    FinancialMetricsResponse
)

router = APIRouter(tags=["financial"])

@router.get("/ratios/{company_name}", response_model=FinancialMetricsResponse)
async def get_financial_ratios(
    company_name: str, 
    year: Optional[int] = Query(None, description="조회할 연도. 지정하지 않으면 직전 연도의 데이터를 조회"),
    db: AsyncSession = Depends(get_db_session)
):
    """회사명으로 재무비율을 조회합니다."""
    controller = FinController(db)
    return await controller.get_financial_ratios(company_name, year)

@router.get("/financial", summary="재무제표 조회 (기본 회사)")
async def get_financial(
    year: Optional[int] = Query(None, description="조회할 연도. 지정하지 않으면 직전 연도의 데이터를 조회"),
    db: AsyncSession = Depends(get_db_session)
):
    """기본 회사의 재무제표를 조회합니다."""
    controller = FinController(db)
    return await controller.get_financial(year=year)

@router.post("/financial", summary="회사명으로 재무제표 조회", response_model=FinancialMetricsResponse)
async def get_financial_by_name(
    payload: CompanyNameRequest,
    year: Optional[int] = Query(None, description="조회할 연도. 지정하지 않으면 직전 연도의 데이터를 조회"),
    db: AsyncSession = Depends(get_db_session)
):
    controller = FinController(db)
    return await controller.get_financial(company_name=payload.company_name, year=year)