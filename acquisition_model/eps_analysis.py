"""
EPS Accretion/Dilution Analysis Module.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum

from .company import Company
from .deal_structure import DealStructure
from .synergies import SynergiesAnalysis


class AccretionDilutionResult(Enum):
    """Result classification."""
    ACCRETIVE = "accretive"
    DILUTIVE = "dilutive"
    NEUTRAL = "neutral"


@dataclass
class EPSAnalysisInputs:
    """Inputs for EPS analysis."""
    # Acquirer data
    acquirer_net_income: float
    acquirer_shares_outstanding: float

    # Target data
    target_net_income: float
    target_shares_outstanding: float

    # Deal structure
    offer_price_per_share: float
    cash_percentage: float
    acquirer_share_price: float
    stock_exchange_ratio: float = 0.0  # If using fixed exchange ratio

    # Financing
    new_debt_amount: float = 0.0
    debt_interest_rate: float = 0.05
    foregone_cash_return: float = 0.02  # Return on cash used

    # Synergies (after-tax)
    synergy_benefit: float = 0.0

    # Other adjustments
    transaction_costs: float = 0.0
    intangible_amortization: float = 0.0  # Annual amortization of acquired intangibles
    tax_rate: float = 0.21


class EPSAccretionDilution:
    """EPS Accretion/Dilution Analysis."""

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

    def calculate_shares_issued(self) -> float:
        """Calculate new shares issued in stock portion of deal."""
        if self.deal.cash_percentage >= 1.0:
            return 0.0

        stock_consideration = self.deal.equity_purchase_price * (1 - self.deal.cash_percentage)
        shares_issued = stock_consideration / self.acquirer.market_data.share_price
        return shares_issued

    def calculate_interest_expense(self) -> float:
        """Calculate new interest expense from deal financing."""
        return self.deal.annual_interest_expense

    def calculate_foregone_interest_income(self) -> float:
        """Calculate foregone interest income from cash used."""
        # Assume 2% return on cash
        return self.deal.acquirer_cash_used * 0.02

    def calculate_intangible_amortization(
        self,
        useful_life_years: int = 10
    ) -> float:
        """Calculate annual amortization of acquired intangibles."""
        # Simplified: assume 30% of purchase price becomes intangibles
        purchase_premium = self.deal.equity_purchase_price - self.target.balance_sheet.total_equity
        new_intangibles = max(0, purchase_premium * 0.30)
        annual_amortization = new_intangibles / useful_life_years
        return annual_amortization

    def calculate_synergy_benefit(self, year: int = 1) -> float:
        """Calculate after-tax synergy benefit for a given year."""
        if self.synergies is None:
            return 0.0

        return self.synergies.get_net_income_impact_by_year(risk_adjusted=True).get(year, 0)

    def run_analysis(
        self,
        year: int = 1,
        include_synergies: bool = True,
        include_intangible_amortization: bool = True,
        intangible_useful_life: int = 10
    ) -> Dict:
        """Run full EPS accretion/dilution analysis."""
        # Standalone EPS
        acquirer_standalone_eps = self.acquirer.eps
        target_standalone_eps = self.target.eps

        # Pro forma net income components
        acquirer_net_income = self.acquirer.income_statement.net_income
        target_net_income = self.target.income_statement.net_income

        # Adjustments
        new_interest_expense = self.calculate_interest_expense()
        foregone_interest = self.calculate_foregone_interest_income()
        interest_tax_shield = new_interest_expense * self.deal.tax_rate

        # After-tax interest cost
        after_tax_interest_cost = new_interest_expense * (1 - self.deal.tax_rate)
        after_tax_foregone_interest = foregone_interest * (1 - self.deal.tax_rate)

        # Intangible amortization
        intangible_amortization = 0.0
        after_tax_amortization = 0.0
        if include_intangible_amortization:
            intangible_amortization = self.calculate_intangible_amortization(intangible_useful_life)
            after_tax_amortization = intangible_amortization * (1 - self.deal.tax_rate)

        # Synergies
        synergy_benefit = 0.0
        if include_synergies and self.synergies:
            synergy_benefit = self.calculate_synergy_benefit(year)

        # Pro forma net income
        pro_forma_net_income = (
            acquirer_net_income +
            target_net_income -
            after_tax_interest_cost -
            after_tax_foregone_interest -
            after_tax_amortization +
            synergy_benefit
        )

        # Pro forma shares
        new_shares_issued = self.calculate_shares_issued()
        pro_forma_shares = self.acquirer.market_data.shares_outstanding + new_shares_issued

        # Pro forma EPS
        pro_forma_eps = pro_forma_net_income / pro_forma_shares

        # Accretion/Dilution
        eps_change = pro_forma_eps - acquirer_standalone_eps
        eps_change_percent = eps_change / acquirer_standalone_eps

        if eps_change > 0.001:  # Small threshold for rounding
            result = AccretionDilutionResult.ACCRETIVE
        elif eps_change < -0.001:
            result = AccretionDilutionResult.DILUTIVE
        else:
            result = AccretionDilutionResult.NEUTRAL

        return {
            "standalone": {
                "acquirer_eps": acquirer_standalone_eps,
                "acquirer_net_income": acquirer_net_income,
                "acquirer_shares": self.acquirer.market_data.shares_outstanding,
                "target_eps": target_standalone_eps,
                "target_net_income": target_net_income,
            },
            "adjustments": {
                "new_interest_expense": new_interest_expense,
                "after_tax_interest_cost": after_tax_interest_cost,
                "foregone_interest_income": foregone_interest,
                "after_tax_foregone_interest": after_tax_foregone_interest,
                "intangible_amortization": intangible_amortization,
                "after_tax_amortization": after_tax_amortization,
                "synergy_benefit": synergy_benefit,
            },
            "pro_forma": {
                "net_income": pro_forma_net_income,
                "shares_outstanding": pro_forma_shares,
                "new_shares_issued": new_shares_issued,
                "eps": pro_forma_eps,
            },
            "accretion_dilution": {
                "eps_change_dollars": eps_change,
                "eps_change_percent": eps_change_percent,
                "result": result.value,
            },
            "year": year,
        }

    def run_multi_year_analysis(
        self,
        years: int = 5,
        include_synergies: bool = True
    ) -> Dict:
        """Run multi-year EPS analysis showing synergy phase-in."""
        results = {}
        for year in range(1, years + 1):
            results[f"year_{year}"] = self.run_analysis(
                year=year,
                include_synergies=include_synergies
            )
        return results

    def calculate_breakeven_synergies(self) -> float:
        """Calculate synergies needed to achieve breakeven EPS."""
        # Run analysis without synergies
        base_analysis = self.run_analysis(include_synergies=False)

        if base_analysis["accretion_dilution"]["result"] == AccretionDilutionResult.ACCRETIVE.value:
            return 0.0  # Already accretive

        # Calculate dilution to overcome
        dilution_dollars = -base_analysis["accretion_dilution"]["eps_change_dollars"]
        pro_forma_shares = base_analysis["pro_forma"]["shares_outstanding"]

        # Synergies needed (after-tax)
        synergies_needed = dilution_dollars * pro_forma_shares

        return synergies_needed

    def calculate_breakeven_price(self, step: float = 1.0) -> float:
        """Calculate maximum offer price for breakeven EPS (with current synergies)."""
        original_price = self.deal.offer_price_per_share
        test_price = original_price

        # Binary search for breakeven
        low = self.target.market_data.share_price  # At least current price
        high = original_price * 2

        for _ in range(50):  # Max iterations
            mid = (low + high) / 2
            self.deal.offer_price_per_share = mid

            analysis = self.run_analysis(include_synergies=True)

            if analysis["accretion_dilution"]["eps_change_dollars"] > 0:
                low = mid
            else:
                high = mid

            if abs(high - low) < 0.01:
                break

        # Restore original price
        breakeven = mid
        self.deal.offer_price_per_share = original_price

        return breakeven

    def sensitivity_analysis(
        self,
        price_range: Tuple[float, float] = (0.9, 1.1),
        cash_range: Tuple[float, float] = (0.0, 1.0),
        steps: int = 5
    ) -> Dict:
        """Run sensitivity analysis on offer price and cash percentage."""
        original_price = self.deal.offer_price_per_share
        original_cash = self.deal.cash_percentage

        results = []

        price_step = (price_range[1] - price_range[0]) / (steps - 1)
        cash_step = (cash_range[1] - cash_range[0]) / (steps - 1)

        for i in range(steps):
            price_mult = price_range[0] + i * price_step
            test_price = original_price * price_mult

            for j in range(steps):
                cash_pct = cash_range[0] + j * cash_step

                self.deal.offer_price_per_share = test_price
                self.deal.cash_percentage = cash_pct

                analysis = self.run_analysis(include_synergies=True)

                results.append({
                    "offer_price": test_price,
                    "cash_percentage": cash_pct,
                    "pro_forma_eps": analysis["pro_forma"]["eps"],
                    "eps_change_percent": analysis["accretion_dilution"]["eps_change_percent"],
                    "result": analysis["accretion_dilution"]["result"],
                })

        # Restore original values
        self.deal.offer_price_per_share = original_price
        self.deal.cash_percentage = original_cash

        return {
            "sensitivity_results": results,
            "base_offer_price": original_price,
            "base_cash_percentage": original_cash,
        }

    def get_analysis_summary(self) -> Dict:
        """Get comprehensive EPS analysis summary."""
        year1 = self.run_analysis(year=1, include_synergies=True)
        year1_no_syn = self.run_analysis(year=1, include_synergies=False)
        breakeven_synergies = self.calculate_breakeven_synergies()

        return {
            "deal_summary": {
                "offer_price": self.deal.offer_price_per_share,
                "equity_value": self.deal.equity_purchase_price,
                "cash_percentage": self.deal.cash_percentage,
                "control_premium": self.deal.control_premium,
            },
            "year_1_with_synergies": year1,
            "year_1_without_synergies": year1_no_syn,
            "multi_year": self.run_multi_year_analysis(years=5),
            "breakeven_synergies_needed": breakeven_synergies,
            "contribution_analysis": self.calculate_contribution_analysis(),
        }

    def calculate_contribution_analysis(self) -> Dict:
        """Calculate relative contribution of each company."""
        acquirer_revenue = self.acquirer.income_statement.revenue
        target_revenue = self.target.income_statement.revenue
        combined_revenue = acquirer_revenue + target_revenue

        acquirer_ebitda = self.acquirer.income_statement.ebitda
        target_ebitda = self.target.income_statement.ebitda
        combined_ebitda = acquirer_ebitda + target_ebitda

        acquirer_ni = self.acquirer.income_statement.net_income
        target_ni = self.target.income_statement.net_income
        combined_ni = acquirer_ni + target_ni

        acquirer_shares = self.acquirer.market_data.shares_outstanding
        new_shares = self.calculate_shares_issued()
        combined_shares = acquirer_shares + new_shares

        return {
            "revenue_contribution": {
                "acquirer_pct": acquirer_revenue / combined_revenue,
                "target_pct": target_revenue / combined_revenue,
            },
            "ebitda_contribution": {
                "acquirer_pct": acquirer_ebitda / combined_ebitda,
                "target_pct": target_ebitda / combined_ebitda,
            },
            "net_income_contribution": {
                "acquirer_pct": acquirer_ni / combined_ni,
                "target_pct": target_ni / combined_ni,
            },
            "ownership": {
                "existing_shareholders_pct": acquirer_shares / combined_shares,
                "new_shareholders_pct": new_shares / combined_shares,
            },
        }
