"""
Valuation Analysis Module - DCF, Trading Comps, Transaction Comps, and Football Field.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math

from .company import Company


@dataclass
class DCFAssumptions:
    """Assumptions for DCF valuation."""
    projection_years: int = 5
    revenue_growth_rates: List[float] = field(default_factory=lambda: [0.10, 0.08, 0.06, 0.05, 0.04])
    ebitda_margins: List[float] = field(default_factory=lambda: [0.20, 0.21, 0.22, 0.22, 0.22])
    capex_percent_revenue: float = 0.04
    da_percent_revenue: float = 0.03
    nwc_percent_revenue: float = 0.10
    tax_rate: float = 0.21
    terminal_growth_rate: float = 0.025
    wacc: float = 0.09


@dataclass
class TradingComp:
    """Trading comparable company data."""
    name: str
    ticker: str
    market_cap: float
    enterprise_value: float
    revenue: float
    ebitda: float
    net_income: float
    shares_outstanding: float

    @property
    def ev_revenue(self) -> float:
        return self.enterprise_value / self.revenue if self.revenue > 0 else 0

    @property
    def ev_ebitda(self) -> float:
        return self.enterprise_value / self.ebitda if self.ebitda > 0 else 0

    @property
    def pe_ratio(self) -> float:
        eps = self.net_income / self.shares_outstanding if self.shares_outstanding > 0 else 0
        share_price = self.market_cap / self.shares_outstanding if self.shares_outstanding > 0 else 0
        return share_price / eps if eps > 0 else 0


@dataclass
class TransactionComp:
    """Transaction comparable data."""
    target_name: str
    acquirer_name: str
    announcement_date: str
    enterprise_value: float
    equity_value: float
    revenue: float
    ebitda: float
    control_premium: float

    @property
    def ev_revenue(self) -> float:
        return self.enterprise_value / self.revenue if self.revenue > 0 else 0

    @property
    def ev_ebitda(self) -> float:
        return self.enterprise_value / self.ebitda if self.ebitda > 0 else 0


class ValuationAnalysis:
    """Comprehensive valuation analysis including multiple methodologies."""

    def __init__(self, target: Company):
        self.target = target
        self.dcf_assumptions = DCFAssumptions()
        self.trading_comps: List[TradingComp] = []
        self.transaction_comps: List[TransactionComp] = []

    def set_dcf_assumptions(self, assumptions: DCFAssumptions) -> None:
        """Set DCF assumptions."""
        self.dcf_assumptions = assumptions

    def add_trading_comp(self, comp: TradingComp) -> None:
        """Add a trading comparable."""
        self.trading_comps.append(comp)

    def add_transaction_comp(self, comp: TransactionComp) -> None:
        """Add a transaction comparable."""
        self.transaction_comps.append(comp)

    def calculate_wacc(
        self,
        risk_free_rate: float = 0.04,
        market_risk_premium: float = 0.055,
        cost_of_debt: float = 0.05,
        debt_weight: float = 0.30,
        tax_rate: float = 0.21
    ) -> float:
        """Calculate Weighted Average Cost of Capital."""
        equity_weight = 1 - debt_weight
        beta = self.target.market_data.beta

        # Cost of Equity (CAPM)
        cost_of_equity = risk_free_rate + beta * market_risk_premium

        # After-tax cost of debt
        after_tax_cost_of_debt = cost_of_debt * (1 - tax_rate)

        # WACC
        wacc = (equity_weight * cost_of_equity) + (debt_weight * after_tax_cost_of_debt)
        return wacc

    def run_dcf_valuation(self) -> Dict:
        """Run discounted cash flow valuation."""
        assumptions = self.dcf_assumptions
        base_revenue = self.target.income_statement.revenue

        # Project cash flows
        projections = []
        cumulative_revenue = base_revenue

        for year in range(assumptions.projection_years):
            growth_rate = assumptions.revenue_growth_rates[min(year, len(assumptions.revenue_growth_rates) - 1)]
            ebitda_margin = assumptions.ebitda_margins[min(year, len(assumptions.ebitda_margins) - 1)]

            revenue = cumulative_revenue * (1 + growth_rate)
            ebitda = revenue * ebitda_margin
            da = revenue * assumptions.da_percent_revenue
            ebit = ebitda - da
            taxes = ebit * assumptions.tax_rate
            nopat = ebit - taxes
            capex = revenue * assumptions.capex_percent_revenue
            delta_nwc = (revenue - cumulative_revenue) * assumptions.nwc_percent_revenue
            fcf = nopat + da - capex - delta_nwc

            projections.append({
                "year": year + 1,
                "revenue": revenue,
                "ebitda": ebitda,
                "ebit": ebit,
                "nopat": nopat,
                "fcf": fcf,
            })

            cumulative_revenue = revenue

        # Terminal Value
        terminal_fcf = projections[-1]["fcf"] * (1 + assumptions.terminal_growth_rate)
        terminal_value = terminal_fcf / (assumptions.wacc - assumptions.terminal_growth_rate)

        # Discount cash flows
        discount_factors = [(1 + assumptions.wacc) ** -(i + 1) for i in range(assumptions.projection_years)]
        pv_fcfs = [proj["fcf"] * df for proj, df in zip(projections, discount_factors)]
        pv_terminal = terminal_value * discount_factors[-1]

        # Enterprise Value
        enterprise_value = sum(pv_fcfs) + pv_terminal

        # Equity Value
        equity_value = enterprise_value - self.target.balance_sheet.net_debt

        # Per Share Value
        implied_share_price = equity_value / self.target.market_data.shares_outstanding

        return {
            "projections": projections,
            "terminal_value": terminal_value,
            "pv_fcfs": pv_fcfs,
            "pv_terminal": pv_terminal,
            "enterprise_value": enterprise_value,
            "equity_value": equity_value,
            "implied_share_price": implied_share_price,
            "assumptions": {
                "wacc": assumptions.wacc,
                "terminal_growth": assumptions.terminal_growth_rate,
                "projection_years": assumptions.projection_years,
            }
        }

    def run_trading_comps(self) -> Dict:
        """Run trading comparables analysis."""
        if not self.trading_comps:
            return {"error": "No trading comparables provided"}

        ev_revenues = [c.ev_revenue for c in self.trading_comps]
        ev_ebitdas = [c.ev_ebitda for c in self.trading_comps]
        pe_ratios = [c.pe_ratio for c in self.trading_comps if c.pe_ratio > 0]

        def calc_stats(values: List[float]) -> Dict:
            if not values:
                return {"min": 0, "max": 0, "median": 0, "mean": 0}
            sorted_vals = sorted(values)
            n = len(sorted_vals)
            return {
                "min": sorted_vals[0],
                "max": sorted_vals[-1],
                "median": sorted_vals[n // 2] if n % 2 else (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2,
                "mean": sum(sorted_vals) / n,
            }

        ev_revenue_stats = calc_stats(ev_revenues)
        ev_ebitda_stats = calc_stats(ev_ebitdas)
        pe_stats = calc_stats(pe_ratios)

        # Implied valuations using median multiples
        target_revenue = self.target.income_statement.revenue
        target_ebitda = self.target.income_statement.ebitda
        target_eps = self.target.eps

        implied_ev_revenue = {
            "low": target_revenue * ev_revenue_stats["min"],
            "median": target_revenue * ev_revenue_stats["median"],
            "high": target_revenue * ev_revenue_stats["max"],
        }

        implied_ev_ebitda = {
            "low": target_ebitda * ev_ebitda_stats["min"],
            "median": target_ebitda * ev_ebitda_stats["median"],
            "high": target_ebitda * ev_ebitda_stats["max"],
        }

        def ev_to_equity(ev: float) -> float:
            return ev - self.target.balance_sheet.net_debt

        def equity_to_share(equity: float) -> float:
            return equity / self.target.market_data.shares_outstanding

        implied_share_price = {
            "ev_revenue": {k: equity_to_share(ev_to_equity(v)) for k, v in implied_ev_revenue.items()},
            "ev_ebitda": {k: equity_to_share(ev_to_equity(v)) for k, v in implied_ev_ebitda.items()},
            "pe": {
                "low": target_eps * pe_stats["min"],
                "median": target_eps * pe_stats["median"],
                "high": target_eps * pe_stats["max"],
            }
        }

        return {
            "comparables": [
                {
                    "name": c.name,
                    "ticker": c.ticker,
                    "ev_revenue": c.ev_revenue,
                    "ev_ebitda": c.ev_ebitda,
                    "pe_ratio": c.pe_ratio,
                }
                for c in self.trading_comps
            ],
            "multiples_stats": {
                "ev_revenue": ev_revenue_stats,
                "ev_ebitda": ev_ebitda_stats,
                "pe": pe_stats,
            },
            "implied_share_price": implied_share_price,
        }

    def run_transaction_comps(self) -> Dict:
        """Run transaction comparables analysis."""
        if not self.transaction_comps:
            return {"error": "No transaction comparables provided"}

        ev_revenues = [c.ev_revenue for c in self.transaction_comps]
        ev_ebitdas = [c.ev_ebitda for c in self.transaction_comps]
        premiums = [c.control_premium for c in self.transaction_comps]

        def calc_stats(values: List[float]) -> Dict:
            if not values:
                return {"min": 0, "max": 0, "median": 0, "mean": 0}
            sorted_vals = sorted(values)
            n = len(sorted_vals)
            return {
                "min": sorted_vals[0],
                "max": sorted_vals[-1],
                "median": sorted_vals[n // 2] if n % 2 else (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2,
                "mean": sum(sorted_vals) / n,
            }

        ev_revenue_stats = calc_stats(ev_revenues)
        ev_ebitda_stats = calc_stats(ev_ebitdas)
        premium_stats = calc_stats(premiums)

        # Implied valuations
        target_revenue = self.target.income_statement.revenue
        target_ebitda = self.target.income_statement.ebitda
        current_price = self.target.market_data.share_price

        implied_ev = {
            "ev_revenue": {
                "low": target_revenue * ev_revenue_stats["min"],
                "median": target_revenue * ev_revenue_stats["median"],
                "high": target_revenue * ev_revenue_stats["max"],
            },
            "ev_ebitda": {
                "low": target_ebitda * ev_ebitda_stats["min"],
                "median": target_ebitda * ev_ebitda_stats["median"],
                "high": target_ebitda * ev_ebitda_stats["max"],
            }
        }

        implied_price_from_premium = {
            "low": current_price * (1 + premium_stats["min"]),
            "median": current_price * (1 + premium_stats["median"]),
            "high": current_price * (1 + premium_stats["max"]),
        }

        return {
            "transactions": [
                {
                    "target": c.target_name,
                    "acquirer": c.acquirer_name,
                    "date": c.announcement_date,
                    "ev_revenue": c.ev_revenue,
                    "ev_ebitda": c.ev_ebitda,
                    "premium": c.control_premium,
                }
                for c in self.transaction_comps
            ],
            "multiples_stats": {
                "ev_revenue": ev_revenue_stats,
                "ev_ebitda": ev_ebitda_stats,
                "control_premium": premium_stats,
            },
            "implied_ev": implied_ev,
            "implied_price_from_premium": implied_price_from_premium,
        }

    def run_52_week_analysis(
        self,
        week_52_high: float,
        week_52_low: float
    ) -> Dict:
        """Analyze valuation relative to 52-week trading range."""
        current_price = self.target.market_data.share_price

        return {
            "current_price": current_price,
            "52_week_high": week_52_high,
            "52_week_low": week_52_low,
            "premium_to_current": 0.0,
            "premium_to_high": (current_price / week_52_high) - 1,
            "premium_to_low": (current_price / week_52_low) - 1,
            "position_in_range": (current_price - week_52_low) / (week_52_high - week_52_low),
        }

    def generate_football_field(
        self,
        offer_price: Optional[float] = None
    ) -> Dict:
        """Generate football field valuation summary."""
        dcf = self.run_dcf_valuation()
        trading = self.run_trading_comps()
        transaction = self.run_transaction_comps()

        valuation_ranges = {
            "dcf": {
                "methodology": "Discounted Cash Flow",
                "low": dcf["implied_share_price"] * 0.85,  # -15% sensitivity
                "mid": dcf["implied_share_price"],
                "high": dcf["implied_share_price"] * 1.15,  # +15% sensitivity
            }
        }

        if "implied_share_price" in trading:
            valuation_ranges["trading_ev_ebitda"] = {
                "methodology": "Trading Comps (EV/EBITDA)",
                "low": trading["implied_share_price"]["ev_ebitda"]["low"],
                "mid": trading["implied_share_price"]["ev_ebitda"]["median"],
                "high": trading["implied_share_price"]["ev_ebitda"]["high"],
            }

        if "implied_price_from_premium" in transaction:
            valuation_ranges["transaction_premium"] = {
                "methodology": "Transaction Comps (Premium)",
                "low": transaction["implied_price_from_premium"]["low"],
                "mid": transaction["implied_price_from_premium"]["median"],
                "high": transaction["implied_price_from_premium"]["high"],
            }

        current_price = self.target.market_data.share_price

        return {
            "current_share_price": current_price,
            "offer_price": offer_price,
            "valuation_ranges": valuation_ranges,
            "premium_analysis": {
                "current_price": current_price,
                "offer_price": offer_price,
                "implied_premium": (offer_price / current_price - 1) if offer_price else None,
            } if offer_price else None
        }

    def get_valuation_summary(self, offer_price: Optional[float] = None) -> Dict:
        """Get comprehensive valuation summary."""
        return {
            "target_company": self.target.name,
            "target_ticker": self.target.ticker,
            "current_metrics": self.target.get_valuation_metrics(),
            "dcf_valuation": self.run_dcf_valuation(),
            "trading_comps": self.run_trading_comps(),
            "transaction_comps": self.run_transaction_comps(),
            "football_field": self.generate_football_field(offer_price),
        }


def create_sample_trading_comps() -> List[TradingComp]:
    """Create sample trading comparables."""
    return [
        TradingComp(
            name="TechPeer Alpha",
            ticker="TPA",
            market_cap=15_000_000_000,
            enterprise_value=17_000_000_000,
            revenue=12_000_000_000,
            ebitda=2_400_000_000,
            net_income=1_440_000_000,
            shares_outstanding=300_000_000
        ),
        TradingComp(
            name="InnoSoft Corp",
            ticker="ISC",
            market_cap=8_000_000_000,
            enterprise_value=9_500_000_000,
            revenue=7_500_000_000,
            ebitda=1_500_000_000,
            net_income=900_000_000,
            shares_outstanding=200_000_000
        ),
        TradingComp(
            name="Digital Solutions Inc",
            ticker="DSI",
            market_cap=12_000_000_000,
            enterprise_value=13_200_000_000,
            revenue=10_000_000_000,
            ebitda=2_200_000_000,
            net_income=1_320_000_000,
            shares_outstanding=240_000_000
        ),
        TradingComp(
            name="CloudTech Systems",
            ticker="CTS",
            market_cap=20_000_000_000,
            enterprise_value=21_500_000_000,
            revenue=14_000_000_000,
            ebitda=3_500_000_000,
            net_income=2_100_000_000,
            shares_outstanding=400_000_000
        ),
    ]


def create_sample_transaction_comps() -> List[TransactionComp]:
    """Create sample transaction comparables."""
    return [
        TransactionComp(
            target_name="DataTech Inc",
            acquirer_name="MegaCorp",
            announcement_date="2024-06-15",
            enterprise_value=8_500_000_000,
            equity_value=7_000_000_000,
            revenue=5_500_000_000,
            ebitda=1_100_000_000,
            control_premium=0.32
        ),
        TransactionComp(
            target_name="SoftwarePro",
            acquirer_name="TechGiant",
            announcement_date="2024-03-20",
            enterprise_value=6_200_000_000,
            equity_value=5_500_000_000,
            revenue=4_000_000_000,
            ebitda=880_000_000,
            control_premium=0.28
        ),
        TransactionComp(
            target_name="CloudBase Systems",
            acquirer_name="Enterprise Inc",
            announcement_date="2023-11-10",
            enterprise_value=11_000_000_000,
            equity_value=9_800_000_000,
            revenue=7_200_000_000,
            ebitda=1_800_000_000,
            control_premium=0.35
        ),
    ]
