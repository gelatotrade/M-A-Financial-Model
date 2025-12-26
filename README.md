# M&A Acquisition Analysis Model

A comprehensive Python-based financial model for analyzing merger and acquisition (M&A) transactions. This model provides institutional-grade analysis capabilities including deal valuation, EPS accretion/dilution, synergies modeling, pro forma financials, and sensitivity analysis.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Model Components](#model-components)
  - [Company Module](#company-module)
  - [Deal Structure](#deal-structure)
  - [Valuation Analysis](#valuation-analysis)
  - [Synergies Analysis](#synergies-analysis)
  - [EPS Accretion/Dilution](#eps-accretiondilution)
  - [Pro Forma Financials](#pro-forma-financials)
  - [Sensitivity Analysis](#sensitivity-analysis)
- [Example Usage](#example-usage)
- [API Reference](#api-reference)
- [Model Methodology](#model-methodology)
- [Best Practices](#best-practices)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Capabilities

- **Deal Valuation**: Multiple valuation methodologies including DCF, trading comps, and transaction comps
- **EPS Accretion/Dilution Analysis**: Comprehensive analysis with multi-year projections
- **Synergies Modeling**: Cost and revenue synergies with phase-in schedules and risk adjustments
- **Pro Forma Financials**: Combined income statement, balance sheet, and cash flow projections
- **Sensitivity Analysis**: Multi-dimensional sensitivity on key deal parameters
- **Sources & Uses**: Complete transaction financing analysis

### Key Benefits

- **No External Dependencies**: Uses Python standard library only
- **Modular Architecture**: Use individual components or the full integrated model
- **Institutional-Grade Methodology**: Follows investment banking best practices
- **Fully Customizable**: Override any assumption or calculation
- **Comprehensive Output**: Detailed metrics, summaries, and executive reports

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/M-A-Financial-Model.git
cd M-A-Financial-Model

# No additional installation required - uses Python standard library
# Optionally install development dependencies
pip install -r requirements.txt
```

### Requirements

- Python 3.8 or higher
- No external dependencies for core functionality

## Quick Start

```python
from acquisition_model import AcquisitionModel
from acquisition_model.core import create_sample_model

# Create a sample model with pre-populated data
model = create_sample_model()

# Generate executive summary
print(model.generate_executive_summary())

# Run full analysis
results = model.run_full_analysis()

# Access specific analyses
eps_analysis = model.run_eps_analysis()
pro_forma = model.generate_pro_forma()
sensitivity = model.run_sensitivity_analysis()
```

## Model Components

### Company Module

The `company` module provides data structures for representing acquirer and target companies.

```python
from acquisition_model.company import (
    Company, CompanyType, IncomeStatement, BalanceSheet, MarketData
)

# Create an income statement
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

# Or create from basic inputs
income_stmt = IncomeStatement.from_basic_inputs(
    revenue=10_000_000_000,
    gross_margin=0.45,
    opex_percent=0.25,
    da_percent=0.04,
    interest_expense=150_000_000,
    interest_income=20_000_000,
    tax_rate=0.21
)

# Create a balance sheet
balance_sheet = BalanceSheet(
    cash_and_equivalents=1_200_000_000,
    accounts_receivable=900_000_000,
    inventory=700_000_000,
    # ... additional fields
)

# Create market data
market_data = MarketData(
    share_price=58.00,
    shares_outstanding=200_000_000,
    beta=1.3,
    dividend_yield=0.01
)

# Create the company
target = Company(
    name="Target Corp",
    ticker="TGT",
    company_type=CompanyType.TARGET,
    income_statement=income_stmt,
    balance_sheet=balance_sheet,
    market_data=market_data
)

# Access key metrics
print(f"EPS: ${target.eps:.2f}")
print(f"P/E Ratio: {target.pe_ratio:.1f}x")
print(f"EV/EBITDA: {target.ev_ebitda:.1f}x")
print(f"Enterprise Value: ${target.enterprise_value:,.0f}")
```

### Deal Structure

The `deal_structure` module handles transaction terms, financing, and sources/uses of funds.

```python
from acquisition_model.deal_structure import (
    DealStructure, DebtTranche, DebtType, TransactionCosts, EquityFinancing
)

# Create debt financing tranches
term_loan = DebtTranche(
    name="Term Loan B",
    debt_type=DebtType.TERM_LOAN_B,
    principal=8_000_000_000,
    interest_rate=0.055,
    maturity_years=7,
    amortization_years=7,  # Amortizing
    origination_fee=0.02
)

senior_notes = DebtTranche(
    name="Senior Notes",
    debt_type=DebtType.SENIOR_NOTES,
    principal=5_000_000_000,
    interest_rate=0.045,
    maturity_years=10,
    amortization_years=None,  # Bullet payment
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

# Create deal structure
deal = DealStructure(
    offer_price_per_share=75.00,
    target_shares_outstanding=200_000_000,
    target_options_dilution=0.02,  # 2% dilution from options
    target_current_price=58.00,
    cash_percentage=0.60,  # 60% cash, 40% stock
    acquirer_cash_used=3_000_000_000,
    debt_tranches=[term_loan, senior_notes],
    transaction_costs=transaction_costs,
    refinance_target_debt=True,
    target_debt_to_refinance=2_300_000_000,
    tax_rate=0.21
)

# Access deal metrics
print(f"Equity Purchase Price: ${deal.equity_purchase_price:,.0f}")
print(f"Control Premium: {deal.control_premium:.1%}")
print(f"Implied EV: ${deal.implied_ev:,.0f}")
print(f"Annual Interest Expense: ${deal.annual_interest_expense:,.0f}")

# Get sources and uses
sources = deal.get_sources_of_funds()
uses = deal.get_uses_of_funds()
```

### Valuation Analysis

The `valuation` module provides multiple valuation methodologies.

```python
from acquisition_model.valuation import (
    ValuationAnalysis, DCFAssumptions, TradingComp, TransactionComp
)

# Initialize valuation analysis
valuation = ValuationAnalysis(target)

# Set DCF assumptions
dcf_assumptions = DCFAssumptions(
    projection_years=5,
    revenue_growth_rates=[0.10, 0.08, 0.06, 0.05, 0.04],
    ebitda_margins=[0.20, 0.21, 0.22, 0.22, 0.22],
    capex_percent_revenue=0.04,
    da_percent_revenue=0.03,
    nwc_percent_revenue=0.10,
    tax_rate=0.21,
    terminal_growth_rate=0.025,
    wacc=0.09
)
valuation.set_dcf_assumptions(dcf_assumptions)

# Run DCF valuation
dcf_result = valuation.run_dcf_valuation()
print(f"DCF Implied Share Price: ${dcf_result['implied_share_price']:.2f}")

# Add trading comparables
valuation.add_trading_comp(TradingComp(
    name="Peer Company A",
    ticker="PEERA",
    market_cap=15_000_000_000,
    enterprise_value=17_000_000_000,
    revenue=12_000_000_000,
    ebitda=2_400_000_000,
    net_income=1_440_000_000,
    shares_outstanding=300_000_000
))

# Run trading comps analysis
trading_result = valuation.run_trading_comps()

# Add transaction comparables
valuation.add_transaction_comp(TransactionComp(
    target_name="Acquired Co",
    acquirer_name="Buyer Inc",
    announcement_date="2024-06-15",
    enterprise_value=8_500_000_000,
    equity_value=7_000_000_000,
    revenue=5_500_000_000,
    ebitda=1_100_000_000,
    control_premium=0.32
))

# Generate football field
football_field = valuation.generate_football_field(offer_price=75.00)
```

### Synergies Analysis

The `synergies` module models cost and revenue synergies with phase-in schedules.

```python
from acquisition_model.synergies import (
    SynergiesAnalysis, SynergyItem, SynergyType,
    SynergyCategory, IntegrationCost
)

# Initialize synergies analysis
synergies = SynergiesAnalysis(projection_years=5, tax_rate=0.21)

# Add cost synergies
synergies.add_cost_synergy(SynergyItem(
    name="Corporate Overhead Elimination",
    synergy_type=SynergyType.COST,
    category=SynergyCategory.CORPORATE_OVERHEAD,
    total_annual_value=200_000_000,  # Run-rate synergy
    phase_in_years=3,
    phase_in_schedule=[0.50, 0.80, 1.00],  # 50% Y1, 80% Y2, 100% Y3
    realization_risk=0.10,  # 10% probability of not achieving
    one_time_cost=50_000_000  # Cost to achieve
))

synergies.add_cost_synergy(SynergyItem(
    name="Headcount Optimization",
    synergy_type=SynergyType.COST,
    category=SynergyCategory.HEADCOUNT_REDUCTION,
    total_annual_value=150_000_000,
    phase_in_years=2,
    phase_in_schedule=[0.60, 1.00],
    realization_risk=0.15
))

# Add revenue synergies
synergies.add_revenue_synergy(SynergyItem(
    name="Cross-Selling Opportunities",
    synergy_type=SynergyType.REVENUE,
    category=SynergyCategory.CROSS_SELLING,
    total_annual_value=300_000_000,
    phase_in_years=4,
    phase_in_schedule=[0.15, 0.40, 0.70, 1.00],
    realization_risk=0.30  # Revenue synergies typically higher risk
))

# Add integration costs
synergies.add_integration_cost(IntegrationCost(
    description="Severance and Restructuring",
    amount=125_000_000,
    year_incurred=1,
    tax_deductible=True
))

# Get synergy summary
summary = synergies.get_synergy_summary()
print(f"Run-Rate Cost Synergies: ${summary['total_run_rate_cost_synergies']:,.0f}")
print(f"Run-Rate Revenue Synergies: ${summary['total_run_rate_revenue_synergies']:,.0f}")
print(f"Total Integration Costs: ${summary['total_integration_costs']:,.0f}")
print(f"Synergy NPV: ${summary['synergy_npv']:,.0f}")

# Get synergies by year
by_year = synergies.get_ebitda_impact_by_year()
for year, impact in by_year.items():
    print(f"Year {year}: ${impact:,.0f}")
```

### EPS Accretion/Dilution

The `eps_analysis` module calculates EPS impact of the transaction.

```python
from acquisition_model.eps_analysis import EPSAccretionDilution

# Initialize EPS analysis
eps_analysis = EPSAccretionDilution(
    acquirer=acquirer,
    target=target,
    deal=deal,
    synergies=synergies
)

# Run analysis for Year 1
result = eps_analysis.run_analysis(
    year=1,
    include_synergies=True,
    include_intangible_amortization=True
)

print(f"Acquirer Standalone EPS: ${result['standalone']['acquirer_eps']:.2f}")
print(f"Pro Forma EPS: ${result['pro_forma']['eps']:.2f}")
print(f"EPS Change: {result['accretion_dilution']['eps_change_percent']:.1%}")
print(f"Result: {result['accretion_dilution']['result'].upper()}")

# Run multi-year analysis
multi_year = eps_analysis.run_multi_year_analysis(years=5)

# Calculate breakeven synergies
breakeven = eps_analysis.calculate_breakeven_synergies()
print(f"Breakeven Synergies Required: ${breakeven:,.0f}")

# Contribution analysis
contribution = eps_analysis.calculate_contribution_analysis()
print(f"Acquirer Revenue Contribution: {contribution['revenue_contribution']['acquirer_pct']:.1%}")
print(f"Target Revenue Contribution: {contribution['revenue_contribution']['target_pct']:.1%}")
```

### Pro Forma Financials

The `pro_forma` module generates combined financial statements.

```python
from acquisition_model.pro_forma import ProFormaFinancials, ProFormaAssumptions

# Set assumptions
assumptions = ProFormaAssumptions(
    projection_years=5,
    acquirer_revenue_growth=0.05,
    target_revenue_growth=0.08,
    acquirer_ebitda_margin=0.20,
    target_ebitda_margin=0.20,
    tax_rate=0.21,
    debt_paydown_percent_fcf=0.50
)

# Initialize pro forma analysis
pro_forma = ProFormaFinancials(
    acquirer=acquirer,
    target=target,
    deal=deal,
    synergies=synergies,
    assumptions=assumptions
)

# Generate combined balance sheet at close
balance_sheet = pro_forma.generate_combined_balance_sheet()
print(f"Total Assets: ${balance_sheet['assets']['total_assets']:,.0f}")
print(f"New Goodwill Created: ${balance_sheet['assets']['new_goodwill_created']:,.0f}")
print(f"Total Debt: ${balance_sheet['liabilities']['long_term_debt']:,.0f}")

# Generate income statement for Year 1
income_stmt = pro_forma.generate_combined_income_statement(year=1)
print(f"Combined Revenue: ${income_stmt['combined_revenue']:,.0f}")
print(f"Combined EBITDA: ${income_stmt['combined_ebitda']:,.0f}")
print(f"Net Income: ${income_stmt['net_income']:,.0f}")

# Generate cash flow projection
cash_flow = pro_forma.generate_cash_flow_projection(year=1)
print(f"Free Cash Flow: ${cash_flow['free_cash_flow']:,.0f}")

# Get credit metrics
credit = pro_forma.generate_credit_metrics(year=1)
print(f"Leverage Ratio: {credit['leverage_ratio']:.2f}x")
print(f"Interest Coverage: {credit['interest_coverage']:.2f}x")

# Generate full projection
full_projection = pro_forma.generate_full_projection()
```

### Sensitivity Analysis

The `sensitivity` module provides comprehensive sensitivity testing.

```python
from acquisition_model.sensitivity import SensitivityAnalysis

# Initialize sensitivity analysis
sensitivity = SensitivityAnalysis(
    acquirer=acquirer,
    target=target,
    deal=deal,
    synergies=synergies
)

# Offer price sensitivity
price_sens = sensitivity.offer_price_sensitivity(
    price_range=(0.8, 1.2),  # 80% to 120% of base price
    steps=9
)

# Financing mix sensitivity
mix_sens = sensitivity.financing_mix_sensitivity(steps=5)

# Interest rate sensitivity
rate_sens = sensitivity.interest_rate_sensitivity(
    rate_change_bps=[-100, -50, 0, 50, 100, 150, 200]
)

# Synergy realization sensitivity
syn_sens = sensitivity.synergy_sensitivity(
    realization_range=(0.5, 1.5),  # 50% to 150% of base case
    steps=5
)

# Two-way sensitivity (price vs cash %)
two_way = sensitivity.price_vs_cash_sensitivity(
    price_steps=5,
    cash_steps=5
)

# WACC sensitivity on DCF valuation
wacc_sens = sensitivity.wacc_sensitivity(
    wacc_range=(0.07, 0.12),
    steps=6
)

# Run full sensitivity suite
full_sensitivity = sensitivity.run_full_sensitivity_suite()
```

## Example Usage

### Basic Analysis

```python
from acquisition_model.core import create_sample_model

# Create sample model
model = create_sample_model()

# Print executive summary
print(model.generate_executive_summary())

# Get deal summary
deal_summary = model.get_deal_summary()

# Get sources and uses
sources_uses = model.get_sources_uses_summary()

# Run valuation
valuation = model.run_valuation_analysis()

# Get EPS analysis
eps = model.run_eps_analysis()

# Generate pro forma
pro_forma = model.generate_pro_forma()

# Export to JSON
model.export_to_json("analysis_output.json")
```

### Custom Scenario

See `examples/custom_scenario.py` for a complete example of creating a custom acquisition scenario from scratch.

## API Reference

### AcquisitionModel

The main orchestration class that ties together all components.

| Method | Description |
|--------|-------------|
| `get_deal_summary()` | Returns high-level deal summary |
| `get_sources_uses_summary()` | Returns sources and uses of funds |
| `run_valuation_analysis()` | Runs comprehensive valuation analysis |
| `get_football_field()` | Returns football field valuation summary |
| `get_synergies_summary()` | Returns synergies analysis summary |
| `run_eps_analysis()` | Runs EPS accretion/dilution analysis |
| `generate_pro_forma()` | Generates pro forma financial projections |
| `run_sensitivity_analysis()` | Runs comprehensive sensitivity analysis |
| `run_full_analysis()` | Runs complete analysis and returns all results |
| `generate_executive_summary()` | Generates text executive summary |
| `export_to_json(filepath)` | Exports full analysis to JSON file |

## Model Methodology

### Valuation Methodologies

1. **Discounted Cash Flow (DCF)**
   - Projects unlevered free cash flows for 5 years
   - Calculates terminal value using perpetuity growth method
   - Discounts at WACC to determine enterprise value

2. **Trading Comparables**
   - Compares target to publicly traded peer companies
   - Analyzes EV/Revenue, EV/EBITDA, and P/E multiples
   - Calculates implied valuation ranges

3. **Transaction Comparables**
   - Analyzes precedent M&A transactions
   - Considers control premiums paid
   - Provides transaction-based valuation benchmarks

### EPS Accretion/Dilution

The model calculates pro forma EPS considering:
- Combined net income of both companies
- New shares issued (if stock consideration)
- Interest expense on new debt financing
- Foregone interest income on cash used
- Amortization of acquired intangibles
- After-tax synergy benefits

### Synergies

- **Cost Synergies**: Flow directly to EBITDA (e.g., headcount, overhead)
- **Revenue Synergies**: Flow through at assumed margin (default 25%)
- **Phase-in Schedules**: Allow for gradual realization over time
- **Risk Adjustment**: Applies probability weighting to synergy estimates
- **NPV Calculation**: Discounts after-tax synergies net of integration costs

### Pro Forma Financials

1. **Balance Sheet (at Close)**
   - Combines both companies' assets and liabilities
   - Adjusts cash for transaction funding
   - Records new goodwill and intangibles
   - Reflects new debt financing

2. **Income Statement (Projected)**
   - Projects revenues with growth assumptions
   - Incorporates synergy benefits
   - Includes new interest expense
   - Calculates pro forma net income

3. **Cash Flow (Projected)**
   - Operating cash flow from net income + D&A - NWC changes
   - Capital expenditures as % of revenue
   - Free cash flow available for debt paydown

## Best Practices

### Input Validation

Always validate your inputs before running the model:

```python
# Check sources = uses
is_balanced, difference = deal.validate_sources_uses()
if not is_balanced:
    print(f"Warning: Sources/Uses imbalance of ${difference:,.0f}")
```

### Scenario Analysis

Run multiple scenarios to understand deal dynamics:

```python
# Conservative case
conservative_synergies = synergies.copy()
# Adjust synergy values...

# Base case
base_model = AcquisitionModel(acquirer, target, deal, synergies)

# Aggressive case
aggressive_synergies = synergies.copy()
# Adjust synergy values...
```

### Documentation

Always document your assumptions:

```python
model = AcquisitionModel(
    acquirer=acquirer,
    target=target,
    deal_structure=deal,
    synergies=synergies,
    model_name="Project Alpha - Base Case v2.1"
)
```

## File Structure

```
M-A-Financial-Model/
├── acquisition_model/
│   ├── __init__.py          # Package initialization
│   ├── company.py            # Company data structures
│   ├── deal_structure.py     # Deal terms and financing
│   ├── valuation.py          # Valuation methodologies
│   ├── synergies.py          # Synergies analysis
│   ├── eps_analysis.py       # EPS accretion/dilution
│   ├── pro_forma.py          # Pro forma financials
│   ├── sensitivity.py        # Sensitivity analysis
│   └── core.py               # Main orchestration class
├── examples/
│   ├── basic_analysis.py     # Basic usage example
│   └── custom_scenario.py    # Custom scenario example
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Typical Deal Metrics

For reference, here are typical ranges for key deal metrics:

| Metric | Typical Range |
|--------|---------------|
| Control Premium | 20-40% |
| EV/EBITDA (Tech) | 10-20x |
| EV/EBITDA (Industrial) | 6-10x |
| Cost Synergies (% of target OpEx) | 5-15% |
| Revenue Synergies (% of target revenue) | 2-5% |
| Synergy Phase-in Period | 2-4 years |
| Integration Costs (% of synergies) | 50-150% |

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Support

For questions or issues, please open a GitHub issue or contact the maintainers.

**Disclaimer**: This model is for educational and analytical purposes only. It should not be used as the sole basis for investment decisions. Always consult with qualified financial advisors for actual M&A transactions.
