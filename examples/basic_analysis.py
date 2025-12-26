#!/usr/bin/env python3
"""
Basic M&A Acquisition Analysis Example

This example demonstrates how to use the acquisition model to analyze
the acquisition of a target company, including:
- Deal structure and financing
- EPS accretion/dilution analysis
- Synergies impact
- Pro forma financials
"""

import sys
sys.path.insert(0, '..')

from acquisition_model import AcquisitionModel
from acquisition_model.company import (
    Company, CompanyType, IncomeStatement, BalanceSheet, MarketData
)
from acquisition_model.deal_structure import (
    DealStructure, DebtTranche, DebtType, TransactionCosts
)
from acquisition_model.synergies import (
    SynergiesAnalysis, SynergyItem, SynergyType, SynergyCategory, IntegrationCost
)
from acquisition_model.valuation import (
    ValuationAnalysis, TradingComp, TransactionComp, DCFAssumptions
)


def create_acquirer() -> Company:
    """Create acquirer company - TechCorp Industries."""
    income_stmt = IncomeStatement(
        revenue=50_000_000_000,
        cost_of_goods_sold=30_000_000_000,
        gross_profit=20_000_000_000,
        operating_expenses=10_000_000_000,
        ebitda=10_000_000_000,
        depreciation_amortization=2_000_000_000,
        ebit=8_000_000_000,
        interest_expense=500_000_000,
        interest_income=100_000_000,
        pretax_income=7_600_000_000,
        tax_expense=1_596_000_000,
        net_income=6_004_000_000
    )

    balance_sheet = BalanceSheet(
        cash_and_equivalents=5_000_000_000,
        accounts_receivable=4_000_000_000,
        inventory=3_000_000_000,
        other_current_assets=1_000_000_000,
        total_current_assets=13_000_000_000,
        property_plant_equipment=15_000_000_000,
        goodwill=8_000_000_000,
        intangible_assets=5_000_000_000,
        other_non_current_assets=2_000_000_000,
        total_assets=43_000_000_000,
        accounts_payable=3_500_000_000,
        short_term_debt=1_000_000_000,
        other_current_liabilities=2_000_000_000,
        total_current_liabilities=6_500_000_000,
        long_term_debt=10_000_000_000,
        other_non_current_liabilities=3_000_000_000,
        total_liabilities=19_500_000_000,
        common_stock=10_000_000_000,
        retained_earnings=13_500_000_000,
        total_equity=23_500_000_000
    )

    market_data = MarketData(
        share_price=150.00,
        shares_outstanding=500_000_000,
        beta=1.1,
        dividend_yield=0.02
    )

    return Company(
        name="TechCorp Industries",
        ticker="TCI",
        company_type=CompanyType.ACQUIRER,
        income_statement=income_stmt,
        balance_sheet=balance_sheet,
        market_data=market_data,
        revenue_growth_rate=0.08
    )


def create_target() -> Company:
    """Create target company - InnovateTech Solutions."""
    income_stmt = IncomeStatement(
        revenue=10_000_000_000,
        cost_of_goods_sold=5_500_000_000,
        gross_profit=4_500_000_000,
        operating_expenses=2_500_000_000,
        ebitda=2_000_000_000,
        depreciation_amortization=400_000_000,
        ebit=1_600_000_000,
        interest_expense=150_000_000,
        interest_income=20_000_000,
        pretax_income=1_470_000_000,
        tax_expense=308_700_000,
        net_income=1_161_300_000
    )

    balance_sheet = BalanceSheet(
        cash_and_equivalents=1_200_000_000,
        accounts_receivable=900_000_000,
        inventory=700_000_000,
        other_current_assets=200_000_000,
        total_current_assets=3_000_000_000,
        property_plant_equipment=3_500_000_000,
        goodwill=1_500_000_000,
        intangible_assets=1_000_000_000,
        other_non_current_assets=500_000_000,
        total_assets=9_500_000_000,
        accounts_payable=800_000_000,
        short_term_debt=300_000_000,
        other_current_liabilities=400_000_000,
        total_current_liabilities=1_500_000_000,
        long_term_debt=2_000_000_000,
        other_non_current_liabilities=500_000_000,
        total_liabilities=4_000_000_000,
        common_stock=2_500_000_000,
        retained_earnings=3_000_000_000,
        total_equity=5_500_000_000
    )

    market_data = MarketData(
        share_price=58.00,
        shares_outstanding=200_000_000,
        beta=1.3,
        dividend_yield=0.01
    )

    return Company(
        name="InnovateTech Solutions",
        ticker="ITS",
        company_type=CompanyType.TARGET,
        income_statement=income_stmt,
        balance_sheet=balance_sheet,
        market_data=market_data,
        revenue_growth_rate=0.12
    )


def create_deal_structure(target: Company) -> DealStructure:
    """Create the deal structure with financing."""

    # Debt tranches
    term_loan = DebtTranche(
        name="Term Loan B",
        debt_type=DebtType.TERM_LOAN_B,
        principal=8_000_000_000,
        interest_rate=0.055,
        maturity_years=7,
        amortization_years=7,
        origination_fee=0.02
    )

    senior_notes = DebtTranche(
        name="Senior Notes",
        debt_type=DebtType.SENIOR_NOTES,
        principal=5_000_000_000,
        interest_rate=0.045,
        maturity_years=10,
        amortization_years=None,  # Bullet
        origination_fee=0.015
    )

    # Transaction costs
    transaction_costs = TransactionCosts(
        advisory_fees=150_000_000,
        legal_fees=50_000_000,
        accounting_fees=25_000_000,
        regulatory_filing_fees=10_000_000,
        other_fees=15_000_000
    )

    return DealStructure(
        offer_price_per_share=75.00,  # ~29% premium
        target_shares_outstanding=target.market_data.shares_outstanding,
        target_options_dilution=0.02,
        target_current_price=target.market_data.share_price,
        cash_percentage=0.60,
        stock_exchange_ratio=0.0,
        acquirer_cash_used=3_000_000_000,
        debt_tranches=[term_loan, senior_notes],
        equity_financing=None,
        transaction_costs=transaction_costs,
        refinance_target_debt=True,
        target_debt_to_refinance=2_300_000_000,
        tax_rate=0.21
    )


def create_synergies() -> SynergiesAnalysis:
    """Create synergies assumptions."""
    analysis = SynergiesAnalysis(projection_years=5, tax_rate=0.21)

    # Cost Synergies
    analysis.add_cost_synergy(SynergyItem(
        name="Corporate Overhead Elimination",
        synergy_type=SynergyType.COST,
        category=SynergyCategory.CORPORATE_OVERHEAD,
        total_annual_value=200_000_000,
        phase_in_years=3,
        phase_in_schedule=[0.50, 0.80, 1.00],
        realization_risk=0.10
    ))

    analysis.add_cost_synergy(SynergyItem(
        name="Headcount Optimization",
        synergy_type=SynergyType.COST,
        category=SynergyCategory.HEADCOUNT_REDUCTION,
        total_annual_value=150_000_000,
        phase_in_years=2,
        phase_in_schedule=[0.60, 1.00],
        realization_risk=0.15
    ))

    analysis.add_cost_synergy(SynergyItem(
        name="IT Systems Consolidation",
        synergy_type=SynergyType.COST,
        category=SynergyCategory.IT_SYSTEMS_INTEGRATION,
        total_annual_value=80_000_000,
        phase_in_years=3,
        phase_in_schedule=[0.20, 0.60, 1.00],
        realization_risk=0.20
    ))

    analysis.add_cost_synergy(SynergyItem(
        name="Procurement Leverage",
        synergy_type=SynergyType.COST,
        category=SynergyCategory.PROCUREMENT_SAVINGS,
        total_annual_value=100_000_000,
        phase_in_years=2,
        phase_in_schedule=[0.40, 1.00],
        realization_risk=0.10
    ))

    # Revenue Synergies
    analysis.add_revenue_synergy(SynergyItem(
        name="Cross-Selling Opportunities",
        synergy_type=SynergyType.REVENUE,
        category=SynergyCategory.CROSS_SELLING,
        total_annual_value=300_000_000,
        phase_in_years=4,
        phase_in_schedule=[0.15, 0.40, 0.70, 1.00],
        realization_risk=0.30
    ))

    analysis.add_revenue_synergy(SynergyItem(
        name="Geographic Expansion",
        synergy_type=SynergyType.REVENUE,
        category=SynergyCategory.GEOGRAPHIC_EXPANSION,
        total_annual_value=200_000_000,
        phase_in_years=4,
        phase_in_schedule=[0.10, 0.30, 0.60, 1.00],
        realization_risk=0.35
    ))

    # Integration Costs
    analysis.add_integration_cost(IntegrationCost(
        description="Severance and Restructuring",
        amount=125_000_000,
        year_incurred=1
    ))

    analysis.add_integration_cost(IntegrationCost(
        description="IT Integration",
        amount=100_000_000,
        year_incurred=1
    ))

    analysis.add_integration_cost(IntegrationCost(
        description="IT Integration Phase 2",
        amount=50_000_000,
        year_incurred=2
    ))

    return analysis


def main():
    """Run the full acquisition analysis."""

    print("=" * 80)
    print("M&A ACQUISITION ANALYSIS MODEL")
    print("TechCorp Industries Acquisition of InnovateTech Solutions")
    print("=" * 80)
    print()

    # Create companies
    acquirer = create_acquirer()
    target = create_target()

    # Create deal structure
    deal = create_deal_structure(target)

    # Create synergies
    synergies = create_synergies()

    # Create the acquisition model
    model = AcquisitionModel(
        acquirer=acquirer,
        target=target,
        deal_structure=deal,
        synergies=synergies,
        model_name="TechCorp / InnovateTech Acquisition"
    )

    # Print executive summary
    print(model.generate_executive_summary())
    print()

    # Print sources and uses
    print("SOURCES AND USES OF FUNDS")
    print("-" * 40)
    sources_uses = model.get_sources_uses_summary()

    print("\nSources:")
    for source, amount in sources_uses["sources"].items():
        if source != "total_sources" and amount > 0:
            print(f"  {source}: ${amount / 1e9:.2f}B")
    print(f"  TOTAL: ${sources_uses['sources']['total_sources'] / 1e9:.2f}B")

    print("\nUses:")
    for use, amount in sources_uses["uses"].items():
        if use != "total_uses" and amount > 0:
            print(f"  {use}: ${amount / 1e9:.2f}B")
    print(f"  TOTAL: ${sources_uses['uses']['total_uses'] / 1e9:.2f}B")

    is_balanced, diff = sources_uses["validation"]
    print(f"\nBalanced: {is_balanced} (difference: ${diff:,.0f})")
    print()

    # Print pro forma metrics
    print("PRO FORMA KEY METRICS")
    print("-" * 40)
    metrics = model.get_pro_forma_summary()

    print(f"\nRevenue:")
    print(f"  At Close: ${metrics['revenue']['at_close'] / 1e9:.1f}B")
    print(f"  Year 5: ${metrics['revenue']['year_5'] / 1e9:.1f}B")
    print(f"  5-Year CAGR: {metrics['revenue']['cagr_5yr']:.1%}")

    print(f"\nEBITDA:")
    print(f"  At Close: ${metrics['ebitda']['at_close'] / 1e9:.2f}B")
    print(f"  Year 5: ${metrics['ebitda']['year_5'] / 1e9:.2f}B")

    print(f"\nLeverage:")
    print(f"  At Close: {metrics['leverage']['at_close']:.2f}x")
    print(f"  Year 5: {metrics['leverage']['year_5']:.2f}x")
    print(f"  Deleveraging: {metrics['leverage']['deleveraging']:.2f}x")

    print(f"\nCoverage:")
    print(f"  At Close: {metrics['coverage']['at_close']:.2f}x")
    print(f"  Year 5: {metrics['coverage']['year_5']:.2f}x")
    print()

    # Print sensitivity summary
    print("SENSITIVITY ANALYSIS SUMMARY")
    print("-" * 40)
    sensitivity = model.get_sensitivity_summary()

    print(f"\nCurrent Deal:")
    print(f"  Offer Price: ${sensitivity['current_deal']['offer_price']:.2f}")
    print(f"  Cash %: {sensitivity['current_deal']['cash_pct']:.0%}")
    print(f"  EPS Result: {sensitivity['current_deal']['is_accretive']}")

    print(f"\nThresholds:")
    if sensitivity['thresholds']['max_accretive_price']:
        print(f"  Max Accretive Price: ${sensitivity['thresholds']['max_accretive_price']:.2f}")
    print(f"  Breakeven Synergies: ${sensitivity['thresholds']['breakeven_synergies'] / 1e6:.0f}M")

    print()
    print("=" * 80)
    print("Analysis Complete")
    print("=" * 80)


if __name__ == "__main__":
    main()
