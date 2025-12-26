#!/usr/bin/env python3
"""
Custom Scenario Example

This example shows how to create a custom acquisition scenario
with your own company data and deal terms.
"""

import sys
sys.path.insert(0, '..')

from acquisition_model import AcquisitionModel
from acquisition_model.company import (
    Company, CompanyType, IncomeStatement, BalanceSheet, MarketData
)
from acquisition_model.deal_structure import (
    DealStructure, DebtTranche, DebtType, TransactionCosts, EquityFinancing
)
from acquisition_model.synergies import (
    SynergiesAnalysis, SynergyItem, SynergyType, SynergyCategory
)


def create_custom_acquirer(
    name: str,
    ticker: str,
    revenue: float,
    ebitda_margin: float,
    net_margin: float,
    share_price: float,
    shares_outstanding: float,
    net_debt: float
) -> Company:
    """
    Create a custom acquirer company with simplified inputs.

    Args:
        name: Company name
        ticker: Stock ticker
        revenue: Annual revenue
        ebitda_margin: EBITDA margin (e.g., 0.20 for 20%)
        net_margin: Net income margin (e.g., 0.12 for 12%)
        share_price: Current share price
        shares_outstanding: Number of shares outstanding
        net_debt: Net debt (debt - cash)
    """
    ebitda = revenue * ebitda_margin
    net_income = revenue * net_margin

    # Estimate other line items
    gross_margin = 0.40
    da_margin = 0.03
    tax_rate = 0.21

    income_stmt = IncomeStatement.from_basic_inputs(
        revenue=revenue,
        gross_margin=gross_margin,
        opex_percent=gross_margin - ebitda_margin,
        da_percent=da_margin,
        interest_expense=net_debt * 0.05 if net_debt > 0 else 0,
        interest_income=abs(net_debt) * 0.02 if net_debt < 0 else 0,
        tax_rate=tax_rate
    )

    # Override net income to match target
    income_stmt = IncomeStatement(
        revenue=income_stmt.revenue,
        cost_of_goods_sold=income_stmt.cost_of_goods_sold,
        gross_profit=income_stmt.gross_profit,
        operating_expenses=income_stmt.operating_expenses,
        ebitda=ebitda,
        depreciation_amortization=income_stmt.depreciation_amortization,
        ebit=income_stmt.ebit,
        interest_expense=income_stmt.interest_expense,
        interest_income=income_stmt.interest_income,
        pretax_income=income_stmt.pretax_income,
        tax_expense=income_stmt.pretax_income - net_income,
        net_income=net_income
    )

    # Simplified balance sheet
    cash = max(0, -net_debt) + revenue * 0.05
    total_debt = max(0, net_debt + cash)

    balance_sheet = BalanceSheet(
        cash_and_equivalents=cash,
        accounts_receivable=revenue * 0.08,
        inventory=revenue * 0.06,
        other_current_assets=revenue * 0.02,
        total_current_assets=cash + revenue * 0.16,
        property_plant_equipment=revenue * 0.30,
        goodwill=revenue * 0.15,
        intangible_assets=revenue * 0.10,
        other_non_current_assets=revenue * 0.05,
        total_assets=cash + revenue * 0.76,
        accounts_payable=revenue * 0.07,
        short_term_debt=total_debt * 0.10,
        other_current_liabilities=revenue * 0.04,
        total_current_liabilities=revenue * 0.11 + total_debt * 0.10,
        long_term_debt=total_debt * 0.90,
        other_non_current_liabilities=revenue * 0.05,
        total_liabilities=revenue * 0.16 + total_debt + revenue * 0.05,
        common_stock=revenue * 0.20,
        retained_earnings=cash + revenue * 0.76 - (revenue * 0.16 + total_debt + revenue * 0.05) - revenue * 0.20,
        total_equity=cash + revenue * 0.76 - (revenue * 0.16 + total_debt + revenue * 0.05)
    )

    market_data = MarketData(
        share_price=share_price,
        shares_outstanding=shares_outstanding,
        beta=1.1,
        dividend_yield=0.02
    )

    return Company(
        name=name,
        ticker=ticker,
        company_type=CompanyType.ACQUIRER,
        income_statement=income_stmt,
        balance_sheet=balance_sheet,
        market_data=market_data
    )


def create_custom_target(
    name: str,
    ticker: str,
    revenue: float,
    ebitda_margin: float,
    net_margin: float,
    share_price: float,
    shares_outstanding: float,
    net_debt: float
) -> Company:
    """Create a custom target company with simplified inputs."""
    # Use same logic as acquirer
    company = create_custom_acquirer(
        name, ticker, revenue, ebitda_margin, net_margin,
        share_price, shares_outstanding, net_debt
    )
    company.company_type = CompanyType.TARGET
    return company


def run_custom_scenario():
    """Run a custom acquisition scenario."""

    print("=" * 80)
    print("CUSTOM ACQUISITION SCENARIO")
    print("=" * 80)
    print()

    # Create custom acquirer
    acquirer = create_custom_acquirer(
        name="MegaCorp Holdings",
        ticker="MEGA",
        revenue=25_000_000_000,      # $25B revenue
        ebitda_margin=0.22,          # 22% EBITDA margin
        net_margin=0.14,             # 14% net margin
        share_price=85.00,           # $85 per share
        shares_outstanding=300_000_000,  # 300M shares
        net_debt=3_000_000_000       # $3B net debt
    )

    # Create custom target
    target = create_custom_target(
        name="GrowthTech Inc",
        ticker="GROW",
        revenue=5_000_000_000,       # $5B revenue
        ebitda_margin=0.18,          # 18% EBITDA margin
        net_margin=0.10,             # 10% net margin
        share_price=42.00,           # $42 per share
        shares_outstanding=100_000_000,  # 100M shares
        net_debt=500_000_000         # $500M net debt
    )

    # Define deal terms
    offer_price = 55.00  # $55 per share (31% premium)

    # Financing structure
    term_loan = DebtTranche(
        name="Term Loan",
        debt_type=DebtType.TERM_LOAN_B,
        principal=4_000_000_000,
        interest_rate=0.06,
        maturity_years=7,
        amortization_years=7
    )

    deal = DealStructure(
        offer_price_per_share=offer_price,
        target_shares_outstanding=target.market_data.shares_outstanding,
        target_current_price=target.market_data.share_price,
        cash_percentage=0.70,  # 70% cash, 30% stock
        acquirer_cash_used=1_500_000_000,
        debt_tranches=[term_loan],
        transaction_costs=TransactionCosts(
            advisory_fees=75_000_000,
            legal_fees=25_000_000,
            accounting_fees=15_000_000,
            regulatory_filing_fees=5_000_000
        ),
        refinance_target_debt=True,
        target_debt_to_refinance=target.balance_sheet.total_debt,
        tax_rate=0.21
    )

    # Define synergies
    synergies = SynergiesAnalysis(projection_years=5)

    synergies.add_cost_synergy(SynergyItem(
        name="Operational Synergies",
        synergy_type=SynergyType.COST,
        category=SynergyCategory.CORPORATE_OVERHEAD,
        total_annual_value=150_000_000,  # $150M run-rate
        phase_in_years=3,
        phase_in_schedule=[0.40, 0.75, 1.00],
        realization_risk=0.15
    ))

    synergies.add_revenue_synergy(SynergyItem(
        name="Revenue Synergies",
        synergy_type=SynergyType.REVENUE,
        category=SynergyCategory.CROSS_SELLING,
        total_annual_value=100_000_000,  # $100M run-rate
        phase_in_years=4,
        phase_in_schedule=[0.20, 0.50, 0.80, 1.00],
        realization_risk=0.30
    ))

    # Create and run the model
    model = AcquisitionModel(
        acquirer=acquirer,
        target=target,
        deal_structure=deal,
        synergies=synergies,
        model_name="MegaCorp / GrowthTech Acquisition"
    )

    # Print results
    print(model.generate_executive_summary())
    print()

    # Show multi-year EPS trajectory
    print("MULTI-YEAR EPS TRAJECTORY")
    print("-" * 50)

    eps_analysis = model.eps_analysis.run_multi_year_analysis(years=5)
    standalone_eps = acquirer.eps

    print(f"{'Year':<10} {'Pro Forma EPS':<15} {'Accretion %':<15} {'Result':<15}")
    print("-" * 50)

    for year in range(1, 6):
        year_data = eps_analysis[f"year_{year}"]
        print(
            f"Year {year:<5} "
            f"${year_data['pro_forma']['eps']:<13.2f} "
            f"{year_data['accretion_dilution']['eps_change_percent']:>+13.1%} "
            f"{year_data['accretion_dilution']['result']:<15}"
        )

    print()
    print("=" * 80)


if __name__ == "__main__":
    run_custom_scenario()
