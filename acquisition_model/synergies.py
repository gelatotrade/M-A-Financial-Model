"""
Synergies Analysis Module - Revenue and Cost Synergies with Phase-in Schedule.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class SynergyType(Enum):
    """Type of synergy."""
    COST = "cost"
    REVENUE = "revenue"


class SynergyCategory(Enum):
    """Category of synergy for detailed breakdown."""
    # Cost Synergies
    HEADCOUNT_REDUCTION = "headcount_reduction"
    FACILITIES_CONSOLIDATION = "facilities_consolidation"
    IT_SYSTEMS_INTEGRATION = "it_systems_integration"
    PROCUREMENT_SAVINGS = "procurement_savings"
    CORPORATE_OVERHEAD = "corporate_overhead"
    MARKETING_OPTIMIZATION = "marketing_optimization"

    # Revenue Synergies
    CROSS_SELLING = "cross_selling"
    GEOGRAPHIC_EXPANSION = "geographic_expansion"
    PRODUCT_BUNDLING = "product_bundling"
    PRICING_OPTIMIZATION = "pricing_optimization"
    CUSTOMER_RETENTION = "customer_retention"
    NEW_MARKET_ACCESS = "new_market_access"


@dataclass
class SynergyItem:
    """Individual synergy item with phase-in schedule."""
    name: str
    synergy_type: SynergyType
    category: SynergyCategory
    total_annual_value: float
    phase_in_years: int = 3
    phase_in_schedule: List[float] = field(default_factory=lambda: [0.30, 0.60, 1.00])
    realization_risk: float = 0.0  # Probability of not achieving
    one_time_cost: float = 0.0  # Cost to achieve synergy

    def get_value_by_year(self, year: int) -> float:
        """Get synergy value for a specific year."""
        if year < 1 or year > self.phase_in_years:
            return self.total_annual_value if year > self.phase_in_years else 0
        return self.total_annual_value * self.phase_in_schedule[year - 1]

    def get_risk_adjusted_value(self, year: int) -> float:
        """Get risk-adjusted synergy value."""
        base_value = self.get_value_by_year(year)
        return base_value * (1 - self.realization_risk)


@dataclass
class IntegrationCost:
    """One-time integration cost."""
    description: str
    amount: float
    year_incurred: int = 1
    tax_deductible: bool = True


class SynergiesAnalysis:
    """Comprehensive synergies analysis with phase-in and risk adjustment."""

    def __init__(self, projection_years: int = 5, tax_rate: float = 0.21):
        self.projection_years = projection_years
        self.tax_rate = tax_rate
        self.cost_synergies: List[SynergyItem] = []
        self.revenue_synergies: List[SynergyItem] = []
        self.integration_costs: List[IntegrationCost] = []
        self.synergy_margin: float = 0.25  # Margin on revenue synergies

    def add_cost_synergy(self, synergy: SynergyItem) -> None:
        """Add a cost synergy item."""
        if synergy.synergy_type != SynergyType.COST:
            raise ValueError("Synergy must be of type COST")
        self.cost_synergies.append(synergy)

    def add_revenue_synergy(self, synergy: SynergyItem) -> None:
        """Add a revenue synergy item."""
        if synergy.synergy_type != SynergyType.REVENUE:
            raise ValueError("Synergy must be of type REVENUE")
        self.revenue_synergies.append(synergy)

    def add_integration_cost(self, cost: IntegrationCost) -> None:
        """Add an integration cost."""
        self.integration_costs.append(cost)

    def get_cost_synergies_by_year(self, risk_adjusted: bool = True) -> Dict[int, float]:
        """Get total cost synergies by year."""
        result = {}
        for year in range(1, self.projection_years + 1):
            total = 0
            for synergy in self.cost_synergies:
                if risk_adjusted:
                    total += synergy.get_risk_adjusted_value(year)
                else:
                    total += synergy.get_value_by_year(year)
            result[year] = total
        return result

    def get_revenue_synergies_by_year(self, risk_adjusted: bool = True) -> Dict[int, float]:
        """Get total revenue synergies by year."""
        result = {}
        for year in range(1, self.projection_years + 1):
            total = 0
            for synergy in self.revenue_synergies:
                if risk_adjusted:
                    total += synergy.get_risk_adjusted_value(year)
                else:
                    total += synergy.get_value_by_year(year)
            result[year] = total
        return result

    def get_ebitda_impact_by_year(self, risk_adjusted: bool = True) -> Dict[int, float]:
        """Get total EBITDA impact from synergies by year."""
        cost_synergies = self.get_cost_synergies_by_year(risk_adjusted)
        revenue_synergies = self.get_revenue_synergies_by_year(risk_adjusted)

        result = {}
        for year in range(1, self.projection_years + 1):
            # Cost synergies flow directly to EBITDA
            cost_impact = cost_synergies.get(year, 0)
            # Revenue synergies flow through at margin
            revenue_impact = revenue_synergies.get(year, 0) * self.synergy_margin
            result[year] = cost_impact + revenue_impact
        return result

    def get_net_income_impact_by_year(self, risk_adjusted: bool = True) -> Dict[int, float]:
        """Get total net income impact from synergies by year."""
        ebitda_impact = self.get_ebitda_impact_by_year(risk_adjusted)

        result = {}
        for year in range(1, self.projection_years + 1):
            # After-tax synergy benefit
            pretax_impact = ebitda_impact.get(year, 0)
            result[year] = pretax_impact * (1 - self.tax_rate)
        return result

    def get_integration_costs_by_year(self) -> Dict[int, float]:
        """Get total integration costs by year."""
        result = {year: 0.0 for year in range(1, self.projection_years + 1)}
        for cost in self.integration_costs:
            if cost.year_incurred in result:
                result[cost.year_incurred] += cost.amount
        return result

    def get_total_integration_costs(self) -> float:
        """Get total integration costs across all years."""
        return sum(c.amount for c in self.integration_costs)

    def get_total_run_rate_synergies(self) -> Dict[str, float]:
        """Get total run-rate synergies at full realization."""
        cost_run_rate = sum(s.total_annual_value for s in self.cost_synergies)
        revenue_run_rate = sum(s.total_annual_value for s in self.revenue_synergies)

        return {
            "cost_synergies": cost_run_rate,
            "revenue_synergies": revenue_run_rate,
            "ebitda_impact": cost_run_rate + (revenue_run_rate * self.synergy_margin),
            "net_income_impact": (cost_run_rate + (revenue_run_rate * self.synergy_margin)) * (1 - self.tax_rate),
        }

    def get_synergy_npv(self, discount_rate: float = 0.09) -> float:
        """Calculate NPV of synergies net of integration costs."""
        net_income_impact = self.get_net_income_impact_by_year(risk_adjusted=True)
        integration_costs = self.get_integration_costs_by_year()

        npv = 0
        for year in range(1, self.projection_years + 1):
            net_benefit = net_income_impact.get(year, 0) - integration_costs.get(year, 0)
            discount_factor = 1 / ((1 + discount_rate) ** year)
            npv += net_benefit * discount_factor

        # Add terminal value of synergies
        run_rate = self.get_total_run_rate_synergies()["net_income_impact"]
        terminal_value = run_rate / discount_rate
        terminal_discount = 1 / ((1 + discount_rate) ** self.projection_years)
        npv += terminal_value * terminal_discount

        return npv

    def get_synergy_breakdown(self) -> Dict:
        """Get detailed synergy breakdown by category."""
        cost_by_category = {}
        for synergy in self.cost_synergies:
            cat = synergy.category.value
            if cat not in cost_by_category:
                cost_by_category[cat] = 0
            cost_by_category[cat] += synergy.total_annual_value

        revenue_by_category = {}
        for synergy in self.revenue_synergies:
            cat = synergy.category.value
            if cat not in revenue_by_category:
                revenue_by_category[cat] = 0
            revenue_by_category[cat] += synergy.total_annual_value

        return {
            "cost_synergies_by_category": cost_by_category,
            "revenue_synergies_by_category": revenue_by_category,
        }

    def get_synergy_summary(self) -> Dict:
        """Get comprehensive synergy summary."""
        run_rate = self.get_total_run_rate_synergies()

        return {
            "total_run_rate_cost_synergies": run_rate["cost_synergies"],
            "total_run_rate_revenue_synergies": run_rate["revenue_synergies"],
            "total_run_rate_ebitda_impact": run_rate["ebitda_impact"],
            "total_run_rate_net_income_impact": run_rate["net_income_impact"],
            "total_integration_costs": self.get_total_integration_costs(),
            "cost_synergies_by_year": self.get_cost_synergies_by_year(),
            "revenue_synergies_by_year": self.get_revenue_synergies_by_year(),
            "ebitda_impact_by_year": self.get_ebitda_impact_by_year(),
            "net_income_impact_by_year": self.get_net_income_impact_by_year(),
            "integration_costs_by_year": self.get_integration_costs_by_year(),
            "synergy_breakdown": self.get_synergy_breakdown(),
            "synergy_npv": self.get_synergy_npv(),
            "years_to_full_realization": max(s.phase_in_years for s in self.cost_synergies + self.revenue_synergies) if self.cost_synergies or self.revenue_synergies else 0,
        }


def create_sample_synergies() -> SynergiesAnalysis:
    """Create sample synergies for demonstration."""
    analysis = SynergiesAnalysis(projection_years=5, tax_rate=0.21)

    # Cost Synergies
    analysis.add_cost_synergy(SynergyItem(
        name="Corporate Overhead Elimination",
        synergy_type=SynergyType.COST,
        category=SynergyCategory.CORPORATE_OVERHEAD,
        total_annual_value=200_000_000,
        phase_in_years=3,
        phase_in_schedule=[0.50, 0.80, 1.00],
        realization_risk=0.10,
        one_time_cost=50_000_000
    ))

    analysis.add_cost_synergy(SynergyItem(
        name="Headcount Optimization",
        synergy_type=SynergyType.COST,
        category=SynergyCategory.HEADCOUNT_REDUCTION,
        total_annual_value=150_000_000,
        phase_in_years=2,
        phase_in_schedule=[0.60, 1.00],
        realization_risk=0.15,
        one_time_cost=75_000_000
    ))

    analysis.add_cost_synergy(SynergyItem(
        name="IT Systems Consolidation",
        synergy_type=SynergyType.COST,
        category=SynergyCategory.IT_SYSTEMS_INTEGRATION,
        total_annual_value=80_000_000,
        phase_in_years=3,
        phase_in_schedule=[0.20, 0.60, 1.00],
        realization_risk=0.20,
        one_time_cost=100_000_000
    ))

    analysis.add_cost_synergy(SynergyItem(
        name="Procurement Leverage",
        synergy_type=SynergyType.COST,
        category=SynergyCategory.PROCUREMENT_SAVINGS,
        total_annual_value=100_000_000,
        phase_in_years=2,
        phase_in_schedule=[0.40, 1.00],
        realization_risk=0.10,
        one_time_cost=10_000_000
    ))

    analysis.add_cost_synergy(SynergyItem(
        name="Facilities Rationalization",
        synergy_type=SynergyType.COST,
        category=SynergyCategory.FACILITIES_CONSOLIDATION,
        total_annual_value=70_000_000,
        phase_in_years=3,
        phase_in_schedule=[0.30, 0.70, 1.00],
        realization_risk=0.15,
        one_time_cost=40_000_000
    ))

    # Revenue Synergies
    analysis.add_revenue_synergy(SynergyItem(
        name="Cross-Selling Opportunities",
        synergy_type=SynergyType.REVENUE,
        category=SynergyCategory.CROSS_SELLING,
        total_annual_value=300_000_000,
        phase_in_years=4,
        phase_in_schedule=[0.15, 0.40, 0.70, 1.00],
        realization_risk=0.30,
        one_time_cost=25_000_000
    ))

    analysis.add_revenue_synergy(SynergyItem(
        name="Geographic Market Expansion",
        synergy_type=SynergyType.REVENUE,
        category=SynergyCategory.GEOGRAPHIC_EXPANSION,
        total_annual_value=200_000_000,
        phase_in_years=4,
        phase_in_schedule=[0.10, 0.30, 0.60, 1.00],
        realization_risk=0.35,
        one_time_cost=50_000_000
    ))

    analysis.add_revenue_synergy(SynergyItem(
        name="Product Bundling",
        synergy_type=SynergyType.REVENUE,
        category=SynergyCategory.PRODUCT_BUNDLING,
        total_annual_value=100_000_000,
        phase_in_years=3,
        phase_in_schedule=[0.25, 0.60, 1.00],
        realization_risk=0.25,
        one_time_cost=15_000_000
    ))

    # Integration Costs
    analysis.add_integration_cost(IntegrationCost(
        description="Severance and Restructuring",
        amount=125_000_000,
        year_incurred=1,
        tax_deductible=True
    ))

    analysis.add_integration_cost(IntegrationCost(
        description="IT Integration",
        amount=100_000_000,
        year_incurred=1,
        tax_deductible=True
    ))

    analysis.add_integration_cost(IntegrationCost(
        description="IT Integration Phase 2",
        amount=50_000_000,
        year_incurred=2,
        tax_deductible=True
    ))

    analysis.add_integration_cost(IntegrationCost(
        description="Facilities Transition",
        amount=40_000_000,
        year_incurred=1,
        tax_deductible=True
    ))

    analysis.add_integration_cost(IntegrationCost(
        description="Rebranding and Marketing",
        amount=35_000_000,
        year_incurred=1,
        tax_deductible=True
    ))

    return analysis
