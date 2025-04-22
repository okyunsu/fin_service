-- 모든 회사의 코드와 이름 조회
SELECT DISTINCT corp_code, corp_name
FROM fin_data
ORDER BY corp_name;


-- 특정 회사 코드의 재무제표 데이터 확인
SELECT DISTINCT corp_code, corp_name, bsns_year, sj_div, sj_nm
FROM fin_data
WHERE corp_code = '01515323'  -- LG에너지솔루션의 회사 코드
ORDER BY bsns_year DESC, sj_div;


-- 회사 코드와 재무비율 데이터 함께 조회
SELECT 
    s.corp_code,
    s.corp_name,
    s.bsns_year,
    ROUND(s.debt_ratio, 2) as debt_ratio,
    ROUND(s.current_ratio, 2) as current_ratio,
    ROUND(s.interest_coverage_ratio, 2) as interest_coverage_ratio,
    ROUND(s.operating_profit_ratio, 2) as operating_profit_ratio,
    ROUND(s.net_profit_ratio, 2) as net_profit_ratio,
    ROUND(s.roe, 2) as roe,
    ROUND(s.roa, 2) as roa,
    ROUND(s.debt_dependency, 2) as debt_dependency,
    ROUND(s.cash_flow_debt_ratio, 2) as cash_flow_debt_ratio,
    ROUND(s.sales_growth, 2) as sales_growth,
    ROUND(s.operating_profit_growth, 2) as operating_profit_growth,
    ROUND(s.eps_growth, 2) as eps_growth
FROM fin_data s
WHERE s.corp_name = 'LG에너지솔루션'
AND s.sj_div = 'RATIO'
ORDER BY s.bsns_year DESC;


CREATE TABLE IF NOT EXISTS fin_data (
    id SERIAL PRIMARY KEY,                    -- 기본 키, 자동 증가
    corp_code VARCHAR(20) NOT NULL,           -- 회사 코드 (DART에서 제공하는 고유 코드)
    corp_name VARCHAR(100) NOT NULL,          -- 회사명
    stock_code VARCHAR(20),                   -- 주식 코드 (거래소 코드)
    rcept_no VARCHAR(20),                     -- 접수번호 (DART 보고서 접수번호)
    reprt_code VARCHAR(20),                   -- 보고서 코드 (사업보고서, 반기보고서 등)
    bsns_year VARCHAR(4) NOT NULL,            -- 사업연도
    sj_div VARCHAR(10),                       -- 재무제표 구분 (BS: 재무상태표, IS: 손익계산서, CF: 현금흐름표)
    sj_nm VARCHAR(100),                       -- 재무제표명 (재무상태표, 손익계산서, 현금흐름표)
    account_nm VARCHAR(100),                  -- 계정과목명
    thstrm_nm VARCHAR(20),                    -- 당기명 (예: 2023년)
    thstrm_amount NUMERIC,                    -- 당기금액
    frmtrm_nm VARCHAR(20),                    -- 전기명 (예: 2022년)
    frmtrm_amount NUMERIC,                    -- 전기금액
    bfefrmtrm_nm VARCHAR(20),                -- 전전기명 (예: 2021년)
    bfefrmtrm_amount NUMERIC,                -- 전전기금액
    ord INTEGER,                              -- 계정과목 정렬순서
    currency VARCHAR(10),                     -- 통화 단위 (KRW, USD 등)
    debt_ratio NUMERIC,                       -- 부채비율 (%)
    current_ratio NUMERIC,                    -- 유동비율 (%)
    interest_coverage_ratio NUMERIC,          -- 이자보상배율 (배)
    operating_profit_ratio NUMERIC,           -- 영업이익률 (%)
    net_profit_ratio NUMERIC,                 -- 순이익률 (%)
    roe NUMERIC,                              -- 자기자본이익률 (ROE, %)
    roa NUMERIC,                              -- 총자산이익률 (ROA, %)
    debt_dependency NUMERIC,                  -- 부채의존도 (%)
    cash_flow_debt_ratio NUMERIC,            -- 현금흐름대부채비율 (%)
    sales_growth NUMERIC,                     -- 매출액증가율 (%)
    operating_profit_growth NUMERIC,          -- 영업이익증가율 (%)
    eps_growth NUMERIC,                       -- EPS증가율 (%)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- 데이터 생성 시간
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- 데이터 수정 시간
    UNIQUE(corp_code, bsns_year, sj_div, account_nm)  -- 회사코드, 사업연도, 재무제표구분, 계정과목명의 조합은 유니크해야 함
);