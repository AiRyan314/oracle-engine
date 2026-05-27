"""The Core Valuation Engine executing Buffett's methodology."""

class ValuationEngine:
    """Engine to analyze 10-year financial data arrays."""
    
    WACC = 0.09
    TERMINAL_GROWTH = 0.025
    
    @classmethod
    def calculate_dcf(cls, fcf_list: list[float], shares: float, current_price: float) -> tuple[float, bool]:
        """Calculate DCF intrinsic value per share and evaluate 25% margin of safety."""
        if len(fcf_list) == 0 or shares <= 0:
            return 0.0, False
            
        intrinsic_value = 0.0
        for t, fcf in enumerate(fcf_list, start=1):
            intrinsic_value += fcf / ((1 + cls.WACC) ** t)
            
        terminal_value = (fcf_list[-1] * (1 + cls.TERMINAL_GROWTH)) / (cls.WACC - cls.TERMINAL_GROWTH)
        intrinsic_value += terminal_value / ((1 + cls.WACC) ** len(fcf_list))
        
        iv_per_share = intrinsic_value / shares
        margin_of_safety_passed = current_price <= (iv_per_share * 0.75)
        return iv_per_share, margin_of_safety_passed

    @staticmethod
    def calculate_roe(net_income_list: list[float], equity_list: list[float]) -> tuple[float, bool]:
        """Calculate 10-year average ROE. Must be strictly > 15%."""
        roes = [ni / eq if eq > 0 else 0 for ni, eq in zip(net_income_list, equity_list)]
        avg_roe = sum(roes) / len(roes) if roes else 0.0
        return avg_roe, avg_roe > 0.15

    @staticmethod
    def calculate_roic(net_income_list: list[float], equity_list: list[float], debt_list: list[float]) -> tuple[float, bool]:
        """Calculate 10-year average ROIC. Must be > 12%."""
        roics = []
        for ni, eq, debt in zip(net_income_list, equity_list, debt_list):
            invested_capital = eq + debt
            roics.append(ni / invested_capital if invested_capital > 0 else 0)
        avg_roic = sum(roics) / len(roics) if roics else 0.0
        return avg_roic, avg_roic > 0.12

    @staticmethod
    def calculate_debt_payoff(current_debt: float, fcf_list: list[float]) -> tuple[float, bool]:
        """Verify debt can be paid off in < 3 years using avg FCF."""
        avg_fcf = sum(fcf_list) / len(fcf_list) if fcf_list else 0.0
        if avg_fcf <= 0:
            return float('inf'), current_debt == 0
        years = current_debt / avg_fcf
        return years, years < 3.0

    @staticmethod
    def calculate_debt_to_equity(current_debt: float, current_equity: float) -> bool:
        """Verify Debt-to-Equity is < 0.5."""
        if current_equity <= 0:
            return False
        return (current_debt / current_equity) < 0.5

    @staticmethod
    def calculate_eps_cagr(eps_list: list[float]) -> tuple[float, bool]:
        """Verify 10-year positive EPS CAGR."""
        if len(eps_list) < 2 or eps_list[0] <= 0:
            return 0.0, False
        cagr = ((eps_list[-1] / eps_list[0]) ** (1 / (len(eps_list) - 1))) - 1
        return cagr, cagr > 0

    @staticmethod
    def calculate_moat_margin(margin_list: list[float]) -> bool:
        """Verify gross margins do not degrade significantly (allow max 5% total drop over 10 years)."""
        if not margin_list: return False
        return margin_list[-1] >= (margin_list[0] * 0.95)

    @staticmethod
    def calculate_share_yield(shares_list: list[float], dividends_list: list[float]) -> bool:
        """Verify current shares < shares 5 years ago, and dividends are paid."""
        if len(shares_list) < 6: return False
        shares_reduced = shares_list[-1] < shares_list[-6]
        pays_divs = sum(dividends_list) > 0
        return shares_reduced and pays_divs

    @classmethod
    def analyze(cls, records: list[dict], current_price: float) -> dict:
        """Run the full Buffett scorecard across 10 years of normalized dict data."""
        records = sorted(records, key=lambda x: x['year'])
        fcf = [r['fcf'] for r in records]
        ni = [r['net_income'] for r in records]
        eq = [r['equity'] for r in records]
        debt = [r['long_term_debt'] for r in records]
        eps = [r['eps'] for r in records]
        gm = [r['gross_margin'] for r in records]
        shares = [r['shares_outstanding'] for r in records]
        div = [r['dividends'] for r in records]

        current_debt = debt[-1]
        current_eq = eq[-1]
        current_shares = shares[-1]

        iv, dcf_pass = cls.calculate_dcf(fcf, current_shares, current_price)
        avg_roe, roe_pass = cls.calculate_roe(ni, eq)
        avg_roic, roic_pass = cls.calculate_roic(ni, eq, debt)
        payoff_yrs, payoff_pass = cls.calculate_debt_payoff(current_debt, fcf)
        de_pass = cls.calculate_debt_to_equity(current_debt, current_eq)
        cagr, cagr_pass = cls.calculate_eps_cagr(eps)
        margin_pass = cls.calculate_moat_margin(gm)
        yield_pass = cls.calculate_share_yield(shares, div)

        passed_all = all([dcf_pass, roe_pass, roic_pass, payoff_pass, de_pass, cagr_pass, margin_pass, yield_pass])

        return {
            "intrinsic_value": iv,
            "margin_of_safety_pass": dcf_pass,
            "roe_pass": roe_pass,
            "roic_pass": roic_pass,
            "debt_payoff_pass": payoff_pass,
            "debt_to_equity_pass": de_pass,
            "eps_cagr_pass": cagr_pass,
            "margin_pass": margin_pass,
            "yield_pass": yield_pass,
            "overall_pass": passed_all
        }
