"""Script to seed the database with 15 highly detailed, mock companies + 10 years of data."""
from db.database import SessionLocal, Base, engine
from db.models import Company, FinancialRecord, AnalysisResult
from core.engine import ValuationEngine

Base.metadata.create_all(bind=engine)
db = SessionLocal()

companies_meta = [
    {"tk": "AAPL", "nm": "Apple Inc", "p": 120.0, "p_fcf": 80, "p_eq": 300, "shr": 16000, "ni": 90, "d": 100},
    {"tk": "MSFT", "nm": "Microsoft", "p": 250.0, "p_fcf": 60, "p_eq": 150, "shr": 7500, "ni": 70, "d": 50},
    {"tk": "KO", "nm": "Coca-Cola", "p": 45.0, "p_fcf": 10, "p_eq": 25, "shr": 4300, "ni": 9, "d": 35},
    {"tk": "AXP", "nm": "Amex", "p": 140.0, "p_fcf": 15, "p_eq": 22, "shr": 750, "ni": 8, "d": 40},
    {"tk": "BAC", "nm": "Bank of Am.", "p": 28.0, "p_fcf": 25, "p_eq": 270, "shr": 8000, "ni": 27, "d": 250},
    {"tk": "OXY", "nm": "Occidental", "p": 60.0, "p_fcf": 12, "p_eq": 18, "shr": 900, "ni": 10, "d": 20},
    {"tk": "CVX", "nm": "Chevron", "p": 150.0, "p_fcf": 30, "p_eq": 160, "shr": 1900, "ni": 35, "d": 15},
    {"tk": "MCO", "nm": "Moody's", "p": 320.0, "p_fcf": 2, "p_eq": 3, "shr": 180, "ni": 1.5, "d": 7},
    {"tk": "KHC", "nm": "KraftHeinz", "p": 35.0, "p_fcf": 3, "p_eq": 50, "shr": 1200, "ni": 2, "d": 20},
    {"tk": "WFC", "nm": "Wells Fargo", "p": 42.0, "p_fcf": 18, "p_eq": 180, "shr": 3800, "ni": 17, "d": 150},
    {"tk": "DVA", "nm": "DaVita", "p": 95.0, "p_fcf": 1.2, "p_eq": 0.5, "shr": 90, "ni": 0.8, "d": 4},
    {"tk": "GM", "nm": "Gen Motors", "p": 38.0, "p_fcf": 10, "p_eq": 65, "shr": 1400, "ni": 9, "d": 80},
    {"tk": "KR", "nm": "Kroger", "p": 45.0, "p_fcf": 4, "p_eq": 10, "shr": 700, "ni": 2.5, "d": 13},
    {"tk": "VRSN", "nm": "Verisign", "p": 200.0, "p_fcf": 0.8, "p_eq": -1.5, "shr": 100, "ni": 0.7, "d": 1.8},
    {"tk": "USB", "nm": "US Bancorp", "p": 35.0, "p_fcf": 7, "p_eq": 50, "shr": 1500, "ni": 6, "d": 40}
]

def seed():
    db.query(AnalysisResult).delete()
    db.query(FinancialRecord).delete()
    db.query(Company).delete()
    db.commit()

    for c in companies_meta:
        comp = Company(ticker=c["tk"], name=c["nm"], current_price=c["p"])
        db.add(comp)
        db.commit()
        db.refresh(comp)

        records_data = []
        for year in range(2014, 2024):
            mult = 1 + ((year - 2014) * 0.05) 
            shr_mult = 1 - ((year - 2014) * 0.02) 
            
            rec = {
                "year": year,
                "revenue": c["ni"] * 5 * mult,
                "net_income": c["ni"] * mult,
                "fcf": c["p_fcf"] * mult,
                "long_term_debt": c["d"] * (1 if year < 2019 else 0.8),
                "shares_outstanding": c["shr"] * shr_mult,
                "eps": (c["ni"] * mult) / (c["shr"] * shr_mult),
                "gross_margin": 0.40 + ((year - 2014) * 0.005),
                "equity": c["p_eq"] * mult,
                "dividends": c["ni"] * 0.1 * mult
            }
            records_data.append(rec)
            db.add(FinancialRecord(company_id=comp.id, **rec))
        
        db.commit()
        
        res = ValuationEngine.analyze(records_data, c["p"])
        db.add(AnalysisResult(company_id=comp.id, **res))
        db.commit()

if __name__ == "__main__":
    seed()
    print("Database seeded with 15 highly detailed mock companies and 150 distinct financial records.")
