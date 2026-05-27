"""SQLAlchemy ORM Models."""
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True)
    name = Column(String)
    current_price = Column(Float)
    records = relationship("FinancialRecord", back_populates="company", cascade="all, delete-orphan")
    analysis = relationship("AnalysisResult", back_populates="company", uselist=False, cascade="all, delete-orphan")

class FinancialRecord(Base):
    __tablename__ = "financial_records"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    year = Column(Integer)
    revenue = Column(Float)
    net_income = Column(Float)
    fcf = Column(Float)
    long_term_debt = Column(Float)
    shares_outstanding = Column(Float)
    eps = Column(Float)
    gross_margin = Column(Float)
    equity = Column(Float)
    dividends = Column(Float)
    company = relationship("Company", back_populates="records")

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    intrinsic_value = Column(Float)
    overall_pass = Column(Boolean)
    margin_of_safety_pass = Column(Boolean)
    roe_pass = Column(Boolean)
    roic_pass = Column(Boolean)
    debt_payoff_pass = Column(Boolean)
    debt_to_equity_pass = Column(Boolean)
    eps_cagr_pass = Column(Boolean)
    margin_pass = Column(Boolean)
    yield_pass = Column(Boolean)
    company = relationship("Company", back_populates="analysis")
