"""
Deal Structure Module - Handles transaction structure, financing mix, and sources/uses.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple
from enum import Enum


class PaymentType(Enum):
    """Type of payment in the transaction."""
    CASH = "cash"
    STOCK = "stock"
    MIXED = "mixed"


class DebtType(Enum):
    """Type of debt financing."""
    TERM_LOAN_A = "term_loan_a"
    TERM_LOAN_B = "term_loan_b"
    SENIOR_NOTES = "senior_notes"
    HIGH_YIELD_BONDS = "high_yield_bonds"
    REVOLVING_CREDIT = "revolving_credit"
    BRIDGE_LOAN = "bridge_loan"


@dataclass
class DebtTranche:
    """Individual debt financing tranche."""
    name: str
    debt_type: DebtType
    principal: float
    interest_rate: float
    maturity_years: int
    amortization_years: Optional[int] = None  # None = bullet
    origination_fee: float = 0.01
    commitment_fee: float = 0.0025  # for revolvers

    @property
    def annual_interest(self) -> float:
        """Calculate annual interest expense."""
        return self.principal * self.interest_rate

    @property
    def annual_amortization(self) -> float:
        """Calculate annual principal amortization."""
        if self.amortization_years is None:
            return 0.0
        return self.principal / self.amortization_years


@dataclass
class EquityFinancing:
    """Equity financing details."""
    new_shares_issued: float
    issue_price: float
    issuance_costs_percent: float = 0.03

    @property
    def gross_proceeds(self) -> float:
        """Gross equity proceeds."""
        return self.new_shares_issued * self.issue_price

    @property
    def issuance_costs(self) -> float:
        """Total equity issuance costs."""
        return self.gross_proceeds * self.issuance_costs_percent

    @property
    def net_proceeds(self) -> float:
        """Net equity proceeds after costs."""
        return self.gross_proceeds - self.issuance_costs


@dataclass
class TransactionCosts:
    """Transaction costs and fees."""
    advisory_fees: float
    legal_fees: float
    accounting_fees: float
    regulatory_filing_fees: float
    other_fees: float = 0.0

    @property
    def total(self) -> float:
        """Total transaction costs."""
        return (
            self.advisory_fees +
            self.legal_fees +
            self.accounting_fees +
            self.regulatory_filing_fees +
            self.other_fees
        )


@dataclass
class DealStructure:
    """Complete deal structure including valuation, financing, and terms."""
    # Deal Valuation
    offer_price_per_share: float
    target_shares_outstanding: float
    target_options_dilution: float = 0.0  # Additional shares from options/RSUs

    # Control Premium Analysis
    target_current_price: float = 0.0

    # Consideration Mix
    cash_percentage: float = 1.0  # 100% cash by default
    stock_exchange_ratio: float = 0.0  # Shares of acquirer per target share

    # Financing Sources
    acquirer_cash_used: float = 0.0
    debt_tranches: List[DebtTranche] = field(default_factory=list)
    equity_financing: Optional[EquityFinancing] = None

    # Transaction Costs
    transaction_costs: Optional[TransactionCosts] = None

    # Target Debt Treatment
    refinance_target_debt: bool = True
    target_debt_to_refinance: float = 0.0

    # Tax Assumptions
    tax_rate: float = 0.21
    interest_tax_shield: bool = True

    @property
    def diluted_target_shares(self) -> float:
        """Target shares including option dilution."""
        return self.target_shares_outstanding * (1 + self.target_options_dilution)

    @property
    def equity_purchase_price(self) -> float:
        """Total equity purchase price."""
        return self.offer_price_per_share * self.diluted_target_shares

    @property
    def control_premium(self) -> float:
        """Control premium over current price."""
        if self.target_current_price <= 0:
            return 0.0
        return (self.offer_price_per_share / self.target_current_price) - 1

    @property
    def implied_ev(self) -> float:
        """Implied enterprise value of target."""
        return self.equity_purchase_price + self.target_debt_to_refinance

    @property
    def cash_consideration(self) -> float:
        """Total cash consideration to target shareholders."""
        return self.equity_purchase_price * self.cash_percentage

    @property
    def stock_consideration_value(self) -> float:
        """Value of stock consideration."""
        return self.equity_purchase_price * (1 - self.cash_percentage)

    @property
    def total_debt_financing(self) -> float:
        """Total new debt raised."""
        return sum(t.principal for t in self.debt_tranches)

    @property
    def total_debt_costs(self) -> float:
        """Total debt origination costs."""
        return sum(t.principal * t.origination_fee for t in self.debt_tranches)

    @property
    def total_equity_financing(self) -> float:
        """Total equity raised."""
        if self.equity_financing is None:
            return 0.0
        return self.equity_financing.net_proceeds

    @property
    def total_transaction_costs(self) -> float:
        """Total transaction costs."""
        costs = self.total_debt_costs
        if self.transaction_costs:
            costs += self.transaction_costs.total
        if self.equity_financing:
            costs += self.equity_financing.issuance_costs
        return costs

    @property
    def annual_interest_expense(self) -> float:
        """Total annual interest expense from new debt."""
        return sum(t.annual_interest for t in self.debt_tranches)

    @property
    def annual_amortization(self) -> float:
        """Total annual debt amortization."""
        return sum(t.annual_amortization for t in self.debt_tranches)

    def get_sources_of_funds(self) -> Dict[str, float]:
        """Get all sources of funds."""
        sources = {
            "acquirer_cash": self.acquirer_cash_used,
        }

        for tranche in self.debt_tranches:
            sources[f"debt_{tranche.name}"] = tranche.principal

        if self.equity_financing:
            sources["equity_issuance"] = self.equity_financing.gross_proceeds

        sources["total_sources"] = sum(sources.values())
        return sources

    def get_uses_of_funds(self) -> Dict[str, float]:
        """Get all uses of funds."""
        uses = {
            "equity_purchase_price": self.equity_purchase_price,
            "refinance_target_debt": self.target_debt_to_refinance,
            "debt_financing_costs": self.total_debt_costs,
        }

        if self.transaction_costs:
            uses["advisory_fees"] = self.transaction_costs.advisory_fees
            uses["legal_fees"] = self.transaction_costs.legal_fees
            uses["other_transaction_costs"] = (
                self.transaction_costs.accounting_fees +
                self.transaction_costs.regulatory_filing_fees +
                self.transaction_costs.other_fees
            )

        if self.equity_financing:
            uses["equity_issuance_costs"] = self.equity_financing.issuance_costs

        uses["total_uses"] = sum(uses.values())
        return uses

    def validate_sources_uses(self) -> Tuple[bool, float]:
        """Validate that sources equal uses."""
        sources = self.get_sources_of_funds()["total_sources"]
        uses = self.get_uses_of_funds()["total_uses"]
        difference = sources - uses
        is_balanced = abs(difference) < 1  # Allow $1 rounding
        return is_balanced, difference

    def get_financing_summary(self) -> Dict[str, any]:
        """Get comprehensive financing summary."""
        sources = self.get_sources_of_funds()
        uses = self.get_uses_of_funds()
        is_balanced, difference = self.validate_sources_uses()

        return {
            "offer_price_per_share": self.offer_price_per_share,
            "equity_purchase_price": self.equity_purchase_price,
            "control_premium": self.control_premium,
            "implied_ev": self.implied_ev,
            "cash_percentage": self.cash_percentage,
            "stock_percentage": 1 - self.cash_percentage,
            "sources": sources,
            "uses": uses,
            "is_balanced": is_balanced,
            "difference": difference,
            "annual_interest_expense": self.annual_interest_expense,
            "total_transaction_costs": self.total_transaction_costs,
        }


def create_sample_deal_structure(
    offer_price: float = 75.0,
    target_shares: float = 200_000_000,
    cash_pct: float = 0.6,
) -> DealStructure:
    """Create a sample deal structure for demonstration."""

    # Calculate equity value
    equity_value = offer_price * target_shares
    cash_needed = equity_value * cash_pct

    # Create debt tranches
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
        offer_price_per_share=offer_price,
        target_shares_outstanding=target_shares,
        target_options_dilution=0.02,
        target_current_price=58.0,
        cash_percentage=cash_pct,
        stock_exchange_ratio=0.0,
        acquirer_cash_used=3_000_000_000,
        debt_tranches=[term_loan, senior_notes],
        equity_financing=None,
        transaction_costs=transaction_costs,
        refinance_target_debt=True,
        target_debt_to_refinance=2_300_000_000,
        tax_rate=0.21
    )
