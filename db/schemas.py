"""Pydantic models for API validation."""
from pydantic import BaseModel
from typing import List, Optional

class RecordSchema(BaseModel):
    year: int
    revenue: float
    net_income: float
    fcf: float
    long_term_debt: float
    shares_outstanding: float
    eps: float
    gross_margin: float
    equity: float
    dividends: float

class AnalyzeRequest(BaseModel):
    ticker: str
    name: str
    current_price: float
    records: List[RecordSchema]

class AnalysisResponse(BaseModel):
    ticker: str
    intrinsic_value: float
    margin_of_safety_pass: bool
    roe_pass: bool
    roic_pass: bool
    debt_payoff_pass: bool
    debt_to_equity_pass: bool
    eps_cagr_pass: bool
    margin_pass: bool
    yield_pass: bool
    overall_pass: bool

    class Config:
        from_attributes = True
