"""
Sensitivity Analysis Module - Multi-dimensional sensitivity analysis for M&A deals.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable
import copy

from .company import Company
from .deal_structure import DealStructure
from .synergies import SynergiesAnalysis
from .eps_analysis import EPSAccretionDilution
from .pro_forma import ProFormaFinancials


@dataclass
class SensitivityRange:
    """Define a range for sensitivity analysis."""
    name: str
    base_value: float
    low_value: float
    high_value: float
    steps: int = 5

    def get_values(self) -> List[float]:
        """Generate list of values across the range."""
        if self.steps == 1:
            return [self.base_value]
        step_size = (self.high_value - self.low_value) / (self.steps - 1)
        return [self.low_value + i * step_size for i in range(self.steps)]


class SensitivityAnalysis:
    """Comprehensive sensitivity analysis for M&A transactions."""

    def __init__(
        self,
        acquirer: Company,
        target: Company,
        deal: DealStructure,
        synergies: Optional[SynergiesAnalysis] = None
    ):
        self.acquirer = acquirer
        self.target = target
        self.deal = deal
        self.synergies = synergies

        # Create analysis objects
        self.eps_analysis = EPSAccretionDilution(
            acquirer, target, deal, synergies
        )
        self.pro_forma = ProFormaFinancials(
            acquirer, target, deal, synergies
        )

    def _deep_copy_deal(self) -> DealStructure:
        """Create a deep copy of the deal structure."""
        return copy.deepcopy(self.deal)

    def offer_price_sensitivity(
        self,
        price_range: Tuple[float, float] = (0.8, 1.2),
        steps: int = 9
    ) -> Dict:
        """Analyze sensitivity to offer price."""
        base_price = self.deal.offer_price_per_share
        results = []

        for mult in [price_range[0] + i * (price_range[1] - price_range[0]) / (steps - 1) for i in range(steps)]:
            test_price = base_price * mult

            # Temporarily modify deal
            original = self.deal.offer_price_per_share
            self.deal.offer_price_per_share = test_price

            # Run EPS analysis
            eps = self.eps_analysis.run_analysis(year=1, include_synergies=True)

            results.append({
                "offer_price": test_price,
                "control_premium": (test_price / self.target.market_data.share_price) - 1,
                "equity_value": test_price * self.deal.diluted_target_shares,
                "pro_forma_eps": eps["pro_forma"]["eps"],
                "eps_accretion_pct": eps["accretion_dilution"]["eps_change_percent"],
                "result": eps["accretion_dilution"]["result"],
            })

            # Restore
            self.deal.offer_price_per_share = original

        return {
            "variable": "offer_price",
            "base_value": base_price,
            "results": results,
        }

    def financing_mix_sensitivity(self, steps: int = 5) -> Dict:
        """Analyze sensitivity to cash vs stock mix."""
        results = []

        for cash_pct in [i / (steps - 1) for i in range(steps)]:
            # Temporarily modify deal
            original = self.deal.cash_percentage
            self.deal.cash_percentage = cash_pct

            # Run EPS analysis
            eps = self.eps_analysis.run_analysis(year=1, include_synergies=True)

            results.append({
                "cash_percentage": cash_pct,
                "stock_percentage": 1 - cash_pct,
                "shares_issued": self.eps_analysis.calculate_shares_issued(),
                "pro_forma_eps": eps["pro_forma"]["eps"],
                "eps_accretion_pct": eps["accretion_dilution"]["eps_change_percent"],
                "result": eps["accretion_dilution"]["result"],
            })

            # Restore
            self.deal.cash_percentage = original

        return {
            "variable": "financing_mix",
            "base_cash_pct": self.deal.cash_percentage,
            "results": results,
        }

    def interest_rate_sensitivity(
        self,
        rate_change_bps: List[int] = [-100, -50, 0, 50, 100, 150, 200]
    ) -> Dict:
        """Analyze sensitivity to interest rates on new debt."""
        results = []
        original_tranches = copy.deepcopy(self.deal.debt_tranches)

        for bps_change in rate_change_bps:
            # Modify interest rates
            for tranche in self.deal.debt_tranches:
                # Find original rate
                for orig in original_tranches:
                    if orig.name == tranche.name:
                        tranche.interest_rate = orig.interest_rate + (bps_change / 10000)
                        break

            # Run analysis
            eps = self.eps_analysis.run_analysis(year=1, include_synergies=True)
            credit = self.pro_forma.generate_credit_metrics(1)

            results.append({
                "rate_change_bps": bps_change,
                "annual_interest_expense": self.deal.annual_interest_expense,
                "pro_forma_eps": eps["pro_forma"]["eps"],
                "eps_accretion_pct": eps["accretion_dilution"]["eps_change_percent"],
                "interest_coverage": credit["interest_coverage"],
            })

        # Restore
        self.deal.debt_tranches = original_tranches

        return {
            "variable": "interest_rates",
            "results": results,
        }

    def synergy_sensitivity(
        self,
        realization_range: Tuple[float, float] = (0.5, 1.5),
        steps: int = 5
    ) -> Dict:
        """Analyze sensitivity to synergy realization."""
        if not self.synergies:
            return {"error": "No synergies defined"}

        results = []
        base_run_rate = self.synergies.get_total_run_rate_synergies()

        for mult in [realization_range[0] + i * (realization_range[1] - realization_range[0]) / (steps - 1) for i in range(steps)]:
            # Scale synergies by multiplier
            scaled_cost = base_run_rate["cost_synergies"] * mult
            scaled_revenue = base_run_rate["revenue_synergies"] * mult
            scaled_ebitda = base_run_rate["ebitda_impact"] * mult
            scaled_ni = base_run_rate["net_income_impact"] * mult

            # Calculate impact on EPS
            base_eps = self.eps_analysis.run_analysis(year=5, include_synergies=False)
            synergy_eps_impact = scaled_ni / base_eps["pro_forma"]["shares_outstanding"]

            pro_forma_eps = base_eps["pro_forma"]["eps"] + synergy_eps_impact

            results.append({
                "realization_pct": mult,
                "run_rate_cost_synergies": scaled_cost,
                "run_rate_revenue_synergies": scaled_revenue,
                "run_rate_ebitda_impact": scaled_ebitda,
                "run_rate_net_income_impact": scaled_ni,
                "implied_pro_forma_eps": pro_forma_eps,
            })

        return {
            "variable": "synergy_realization",
            "base_run_rate": base_run_rate,
            "results": results,
        }

    def two_way_sensitivity(
        self,
        var1_name: str,
        var1_values: List[float],
        var2_name: str,
        var2_values: List[float]
    ) -> Dict:
        """Run two-way sensitivity analysis."""
        results = []

        for v1 in var1_values:
            for v2 in var2_values:
                # Set variables
                original_v1 = None
                original_v2 = None

                if var1_name == "offer_price":
                    original_v1 = self.deal.offer_price_per_share
                    self.deal.offer_price_per_share = v1
                elif var1_name == "cash_pct":
                    original_v1 = self.deal.cash_percentage
                    self.deal.cash_percentage = v1

                if var2_name == "offer_price":
                    original_v2 = self.deal.offer_price_per_share
                    self.deal.offer_price_per_share = v2
                elif var2_name == "cash_pct":
                    original_v2 = self.deal.cash_percentage
                    self.deal.cash_percentage = v2

                # Run analysis
                eps = self.eps_analysis.run_analysis(year=1, include_synergies=True)

                results.append({
                    var1_name: v1,
                    var2_name: v2,
                    "pro_forma_eps": eps["pro_forma"]["eps"],
                    "eps_accretion_pct": eps["accretion_dilution"]["eps_change_percent"],
                    "result": eps["accretion_dilution"]["result"],
                })

                # Restore
                if var1_name == "offer_price" and original_v1:
                    self.deal.offer_price_per_share = original_v1
                elif var1_name == "cash_pct" and original_v1:
                    self.deal.cash_percentage = original_v1

                if var2_name == "offer_price" and original_v2:
                    self.deal.offer_price_per_share = original_v2
                elif var2_name == "cash_pct" and original_v2:
                    self.deal.cash_percentage = original_v2

        return {
            "var1": var1_name,
            "var1_values": var1_values,
            "var2": var2_name,
            "var2_values": var2_values,
            "results": results,
        }

    def price_vs_cash_sensitivity(self, price_steps: int = 5, cash_steps: int = 5) -> Dict:
        """Standard price vs cash percentage sensitivity matrix."""
        base_price = self.deal.offer_price_per_share

        price_values = [base_price * (0.9 + 0.05 * i) for i in range(price_steps)]
        cash_values = [i / (cash_steps - 1) for i in range(cash_steps)]

        return self.two_way_sensitivity(
            "offer_price", price_values,
            "cash_pct", cash_values
        )

    def wacc_sensitivity(
        self,
        wacc_range: Tuple[float, float] = (0.07, 0.12),
        steps: int = 6
    ) -> Dict:
        """Analyze sensitivity of DCF valuation to WACC."""
        from .valuation import ValuationAnalysis, DCFAssumptions

        valuation = ValuationAnalysis(self.target)
        results = []

        for wacc in [wacc_range[0] + i * (wacc_range[1] - wacc_range[0]) / (steps - 1) for i in range(steps)]:
            assumptions = DCFAssumptions(wacc=wacc)
            valuation.set_dcf_assumptions(assumptions)

            dcf = valuation.run_dcf_valuation()

            results.append({
                "wacc": wacc,
                "enterprise_value": dcf["enterprise_value"],
                "equity_value": dcf["equity_value"],
                "implied_share_price": dcf["implied_share_price"],
                "premium_to_offer": (self.deal.offer_price_per_share / dcf["implied_share_price"]) - 1,
            })

        return {
            "variable": "wacc",
            "offer_price": self.deal.offer_price_per_share,
            "results": results,
        }

    def terminal_growth_sensitivity(
        self,
        growth_range: Tuple[float, float] = (0.015, 0.035),
        steps: int = 5
    ) -> Dict:
        """Analyze sensitivity of DCF valuation to terminal growth rate."""
        from .valuation import ValuationAnalysis, DCFAssumptions

        valuation = ValuationAnalysis(self.target)
        results = []

        for tgr in [growth_range[0] + i * (growth_range[1] - growth_range[0]) / (steps - 1) for i in range(steps)]:
            assumptions = DCFAssumptions(terminal_growth_rate=tgr)
            valuation.set_dcf_assumptions(assumptions)

            dcf = valuation.run_dcf_valuation()

            results.append({
                "terminal_growth_rate": tgr,
                "terminal_value": dcf["terminal_value"],
                "enterprise_value": dcf["enterprise_value"],
                "implied_share_price": dcf["implied_share_price"],
            })

        return {
            "variable": "terminal_growth",
            "results": results,
        }

    def run_full_sensitivity_suite(self) -> Dict:
        """Run complete sensitivity analysis suite."""
        return {
            "offer_price": self.offer_price_sensitivity(),
            "financing_mix": self.financing_mix_sensitivity(),
            "interest_rates": self.interest_rate_sensitivity(),
            "synergies": self.synergy_sensitivity() if self.synergies else None,
            "price_vs_cash_matrix": self.price_vs_cash_sensitivity(),
            "wacc": self.wacc_sensitivity(),
            "terminal_growth": self.terminal_growth_sensitivity(),
        }

    def get_sensitivity_summary(self) -> Dict:
        """Get summary of key sensitivity insights."""
        price_sens = self.offer_price_sensitivity(steps=3)
        mix_sens = self.financing_mix_sensitivity(steps=3)

        # Find accretion thresholds
        accretive_prices = [r for r in price_sens["results"] if r["result"] == "accretive"]
        max_accretive_price = max(r["offer_price"] for r in accretive_prices) if accretive_prices else None

        accretive_cash = [r for r in mix_sens["results"] if r["result"] == "accretive"]

        return {
            "current_deal": {
                "offer_price": self.deal.offer_price_per_share,
                "cash_pct": self.deal.cash_percentage,
                "is_accretive": self.eps_analysis.run_analysis()["accretion_dilution"]["result"],
            },
            "thresholds": {
                "max_accretive_price": max_accretive_price,
                "breakeven_synergies": self.eps_analysis.calculate_breakeven_synergies(),
            },
            "key_drivers": [
                "Offer price",
                "Cash vs stock mix",
                "Synergy realization",
                "Interest rates on financing",
            ]
        }
