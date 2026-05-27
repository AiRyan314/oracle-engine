"""FastAPI Application Entrypoint."""
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from db.database import engine, Base, get_db
from db.models import Company, FinancialRecord, AnalysisResult
from db.schemas import AnalyzeRequest, AnalysisResponse
from core.engine import ValuationEngine
from core.auth import verify_jwt, create_jwt

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Oracle-Engine API")

def get_current_user(authorization: str = Header(None)):
    """Middleware logic to validate custom JWT."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token format")
    token = authorization.split(" ")[1]
    try:
        payload = verify_jwt(token)
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/api/v1/token")
def get_test_token():
    """Generates a valid token for testing purposes."""
    return {"access_token": create_jwt({"user": "buffett"})}

@app.post("/api/v1/analyze", response_model=AnalysisResponse)
def analyze_company(request: AnalyzeRequest, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """Ingests 10-year data, runs Buffett algorithm, and saves results."""
    if len(request.records) != 10:
        raise HTTPException(status_code=422, detail="Exactly 10 years of data required.")
        
    records_dict = [r.model_dump() for r in request.records]
    results = ValuationEngine.analyze(records_dict, request.current_price)
    
    # Store in DB
    company = db.query(Company).filter(Company.ticker == request.ticker).first()
    if not company:
        company = Company(ticker=request.ticker, name=request.name, current_price=request.current_price)
        db.add(company)
        db.commit()
        db.refresh(company)
        
        for r in request.records:
            db_record = FinancialRecord(company_id=company.id, **r.model_dump())
            db.add(db_record)
            
    analysis = AnalysisResult(company_id=company.id, **results)
    db.add(analysis)
    db.commit()
    
    return {**results, "ticker": request.ticker}

@app.get("/api/v1/portfolio", response_model=list[AnalysisResponse])
def get_portfolio(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """Returns all analyzed stocks that passed all Buffett criteria."""
    passing_results = db.query(AnalysisResult).filter(AnalysisResult.overall_pass == True).all()
    response = []
    for res in passing_results:
        res_dict = {c.name: getattr(res, c.name) for c in res.__table__.columns}
        res_dict["ticker"] = res.company.ticker
        response.append(res_dict)
    return response
