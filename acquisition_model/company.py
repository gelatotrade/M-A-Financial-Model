"""
Company data structures for M&A analysis.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List
from enum import Enum


class CompanyType(Enum):
    """Type of company in the transaction."""
    ACQUIRER = "acquirer"
    TARGET = "target"


@dataclass
class IncomeStatement:
    """Annual income statement data."""
    revenue: float
    cost_of_goods_sold: float
    gross_profit: float
    operating_expenses: float
    ebitda: float
    depreciation_amortization: float
    ebit: float
    interest_expense: float
    interest_income: float
    pretax_income: float
    tax_expense: float
    net_income: float

    @classmethod
    def from_basic_inputs(
        cls,
        revenue: float,
        gross_margin: float,
        opex_percent: float,
        da_percent: float,
        interest_expense: float,
        interest_income: float,
        tax_rate: float
    ) -> "IncomeStatement":
        """Create income statement from basic inputs and assumptions."""
        gross_profit = revenue * gross_margin
        cost_of_goods_sold = revenue - gross_profit
        operating_expenses = revenue * opex_percent
        ebitda = gross_profit - operating_expenses
        depreciation_amortization = revenue * da_percent
        ebit = ebitda - depreciation_amortization
        pretax_income = ebit - interest_expense + interest_income
        tax_expense = max(0, pretax_income * tax_rate)
        net_income = pretax_income - tax_expense

        return cls(
            revenue=revenue,
            cost_of_goods_sold=cost_of_goods_sold,
            gross_profit=gross_profit,
            operating_expenses=operating_expenses,
            ebitda=ebitda,
            depreciation_amortization=depreciation_amortization,
            ebit=ebit,
            interest_expense=interest_expense,
            interest_income=interest_income,
            pretax_income=pretax_income,
            tax_expense=tax_expense,
            net_income=net_income
        )


@dataclass
class BalanceSheet:
    """Balance sheet data."""
    # Assets
    cash_and_equivalents: float
    accounts_receivable: float
    inventory: float
    other_current_assets: float
    total_current_assets: float

    property_plant_equipment: float
    goodwill: float
    intangible_assets: float
    other_non_current_assets: float
    total_assets: float

    # Liabilities
    accounts_payable: float
    short_term_debt: float
    other_current_liabilities: float
    total_current_liabilities: float

    long_term_debt: float
    other_non_current_liabilities: float
    total_liabilities: float

    # Equity
    common_stock: float
    retained_earnings: float
    total_equity: float

    @property
    def net_debt(self) -> float:
        """Calculate net debt (total debt - cash)."""
        return self.short_term_debt + self.long_term_debt - self.cash_and_equivalents

    @property
    def total_debt(self) -> float:
        """Total debt including short and long term."""
        return self.short_term_debt + self.long_term_debt

    @property
    def net_working_capital(self) -> float:
        """Net working capital (current assets - current liabilities)."""
        return self.total_current_assets - self.total_current_liabilities


@dataclass
class MarketData:
    """Market and trading data for a company."""
    share_price: float
    shares_outstanding: float
    beta: float = 1.0
    dividend_yield: float = 0.0

    @property
    def market_cap(self) -> float:
        """Market capitalization."""
        return self.share_price * self.shares_outstanding

    @property
    def diluted_shares(self) -> float:
        """Diluted shares outstanding (simplified, same as basic for now)."""
        return self.shares_outstanding


@dataclass
class Company:
    """Complete company profile for M&A analysis."""
    name: str
    ticker: str
    company_type: CompanyType
    income_statement: IncomeStatement
    balance_sheet: BalanceSheet
    market_data: MarketData

    # Growth assumptions
    revenue_growth_rate: float = 0.05
    margin_assumptions: Dict[str, float] = field(default_factory=dict)

    @property
    def enterprise_value(self) -> float:
        """Calculate enterprise value."""
        return (
            self.market_data.market_cap +
            self.balance_sheet.net_debt +
            self.balance_sheet.other_non_current_liabilities  # minority interest, preferred, etc.
        )

    @property
    def eps(self) -> float:
        """Earnings per share."""
        return self.income_statement.net_income / self.market_data.shares_outstanding

    @property
    def pe_ratio(self) -> float:
        """Price to earnings ratio."""
        if self.eps <= 0:
            return float('inf')
        return self.market_data.share_price / self.eps

    @property
    def ev_ebitda(self) -> float:
        """EV/EBITDA multiple."""
        if self.income_statement.ebitda <= 0:
            return float('inf')
        return self.enterprise_value / self.income_statement.ebitda

    @property
    def ev_revenue(self) -> float:
        """EV/Revenue multiple."""
        return self.enterprise_value / self.income_statement.revenue

    def get_valuation_metrics(self) -> Dict[str, float]:
        """Get all valuation metrics."""
        return {
            "market_cap": self.market_data.market_cap,
            "enterprise_value": self.enterprise_value,
            "share_price": self.market_data.share_price,
            "shares_outstanding": self.market_data.shares_outstanding,
            "eps": self.eps,
            "pe_ratio": self.pe_ratio,
            "ev_ebitda": self.ev_ebitda,
            "ev_revenue": self.ev_revenue,
            "net_debt": self.balance_sheet.net_debt,
        }


def create_sample_acquirer() -> Company:
    """Create a sample acquirer company for demonstration."""
    income_stmt = IncomeStatement(
        revenue=50_000_000_000,  # $50B
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


def create_sample_target() -> Company:
    """Create a sample target company for demonstration."""
    income_stmt = IncomeStatement(
        revenue=10_000_000_000,  # $10B
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
