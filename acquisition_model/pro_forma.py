"""
Pro Forma Financial Statements Module.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .company import Company, IncomeStatement, BalanceSheet
from .deal_structure import DealStructure
from .synergies import SynergiesAnalysis


@dataclass
class ProFormaAssumptions:
    """Assumptions for pro forma projections."""
    projection_years: int = 5
    acquirer_revenue_growth: float = 0.05
    target_revenue_growth: float = 0.08
    acquirer_ebitda_margin: float = 0.20
    target_ebitda_margin: float = 0.20
    da_percent_revenue: float = 0.03
    capex_percent_revenue: float = 0.04
    nwc_percent_revenue: float = 0.10
    tax_rate: float = 0.21
    debt_paydown_percent_fcf: float = 0.50  # % of FCF used for debt paydown


class ProFormaFinancials:
    """Generate pro forma financial statements for combined entity."""

    def __init__(
        self,
        acquirer: Company,
        target: Company,
        deal: DealStructure,
        synergies: Optional[SynergiesAnalysis] = None,
        assumptions: Optional[ProFormaAssumptions] = None
    ):
        self.acquirer = acquirer
        self.target = target
        self.deal = deal
        self.synergies = synergies
        self.assumptions = assumptions or ProFormaAssumptions()

    def generate_combined_income_statement(self, year: int = 0) -> Dict:
        """Generate combined income statement for a given year (0 = deal close)."""
        # Base financials
        acq_revenue = self.acquirer.income_statement.revenue
        tgt_revenue = self.target.income_statement.revenue

        acq_ebitda = self.acquirer.income_statement.ebitda
        tgt_ebitda = self.target.income_statement.ebitda

        # Apply growth for future years
        if year > 0:
            acq_growth = (1 + self.assumptions.acquirer_revenue_growth) ** year
            tgt_growth = (1 + self.assumptions.target_revenue_growth) ** year
            acq_revenue *= acq_growth
            tgt_revenue *= tgt_growth
            acq_ebitda = acq_revenue * self.assumptions.acquirer_ebitda_margin
            tgt_ebitda = tgt_revenue * self.assumptions.target_ebitda_margin

        combined_revenue = acq_revenue + tgt_revenue
        combined_ebitda = acq_ebitda + tgt_ebitda

        # Add synergies
        synergy_ebitda_impact = 0
        synergy_revenue = 0
        if self.synergies and year > 0:
            synergy_ebitda_impact = self.synergies.get_ebitda_impact_by_year().get(year, 0)
            synergy_revenue = self.synergies.get_revenue_synergies_by_year().get(year, 0)

        adjusted_revenue = combined_revenue + synergy_revenue
        adjusted_ebitda = combined_ebitda + synergy_ebitda_impact

        # D&A
        da = adjusted_revenue * self.assumptions.da_percent_revenue
        ebit = adjusted_ebitda - da

        # Interest expense (original + new from deal)
        original_interest = (
            self.acquirer.income_statement.interest_expense +
            self.target.income_statement.interest_expense
        )

        # Adjust for refinanced target debt
        if self.deal.refinance_target_debt:
            original_interest -= self.target.income_statement.interest_expense

        new_deal_interest = self.deal.annual_interest_expense
        total_interest = original_interest + new_deal_interest

        # Interest income (reduced by cash used)
        original_interest_income = (
            self.acquirer.income_statement.interest_income +
            self.target.income_statement.interest_income
        )
        foregone_interest = self.deal.acquirer_cash_used * 0.02
        interest_income = max(0, original_interest_income - foregone_interest)

        # Pre-tax income
        pretax_income = ebit - total_interest + interest_income

        # Integration costs (year 1 only typically)
        integration_costs = 0
        if self.synergies and year > 0:
            integration_costs = self.synergies.get_integration_costs_by_year().get(year, 0)

        adjusted_pretax = pretax_income - integration_costs

        # Taxes
        tax_expense = max(0, adjusted_pretax * self.assumptions.tax_rate)
        net_income = adjusted_pretax - tax_expense

        return {
            "year": year,
            "acquirer_revenue": acq_revenue,
            "target_revenue": tgt_revenue,
            "synergy_revenue": synergy_revenue,
            "combined_revenue": adjusted_revenue,
            "acquirer_ebitda": acq_ebitda,
            "target_ebitda": tgt_ebitda,
            "synergy_ebitda": synergy_ebitda_impact,
            "combined_ebitda": adjusted_ebitda,
            "ebitda_margin": adjusted_ebitda / adjusted_revenue,
            "depreciation_amortization": da,
            "ebit": ebit,
            "interest_expense": total_interest,
            "interest_income": interest_income,
            "pretax_income": pretax_income,
            "integration_costs": integration_costs,
            "adjusted_pretax_income": adjusted_pretax,
            "tax_expense": tax_expense,
            "net_income": net_income,
            "net_income_margin": net_income / adjusted_revenue,
        }

    def generate_combined_balance_sheet(self) -> Dict:
        """Generate pro forma combined balance sheet at close."""
        acq_bs = self.acquirer.balance_sheet
        tgt_bs = self.target.balance_sheet

        # Cash adjustment
        combined_cash = (
            acq_bs.cash_and_equivalents +
            tgt_bs.cash_and_equivalents -
            self.deal.acquirer_cash_used
        )

        # Current assets
        accounts_receivable = acq_bs.accounts_receivable + tgt_bs.accounts_receivable
        inventory = acq_bs.inventory + tgt_bs.inventory
        other_current = acq_bs.other_current_assets + tgt_bs.other_current_assets
        total_current_assets = combined_cash + accounts_receivable + inventory + other_current

        # Fixed assets
        ppe = acq_bs.property_plant_equipment + tgt_bs.property_plant_equipment

        # Goodwill calculation
        purchase_premium = self.deal.equity_purchase_price - tgt_bs.total_equity
        existing_goodwill = acq_bs.goodwill + tgt_bs.goodwill
        new_goodwill = max(0, purchase_premium)
        total_goodwill = existing_goodwill + new_goodwill

        # Intangibles (simplified - assume 30% of premium goes to identifiable intangibles)
        identifiable_intangibles = purchase_premium * 0.30
        total_intangibles = acq_bs.intangible_assets + tgt_bs.intangible_assets + identifiable_intangibles

        other_non_current = acq_bs.other_non_current_assets + tgt_bs.other_non_current_assets
        total_assets = total_current_assets + ppe + total_goodwill + total_intangibles + other_non_current

        # Current liabilities
        accounts_payable = acq_bs.accounts_payable + tgt_bs.accounts_payable

        # Short-term debt - target debt refinanced
        if self.deal.refinance_target_debt:
            short_term_debt = acq_bs.short_term_debt
        else:
            short_term_debt = acq_bs.short_term_debt + tgt_bs.short_term_debt

        other_current_liab = acq_bs.other_current_liabilities + tgt_bs.other_current_liabilities
        total_current_liabilities = accounts_payable + short_term_debt + other_current_liab

        # Long-term debt
        if self.deal.refinance_target_debt:
            existing_lt_debt = acq_bs.long_term_debt
        else:
            existing_lt_debt = acq_bs.long_term_debt + tgt_bs.long_term_debt

        new_debt = self.deal.total_debt_financing
        total_lt_debt = existing_lt_debt + new_debt

        other_lt_liab = acq_bs.other_non_current_liabilities + tgt_bs.other_non_current_liabilities
        total_liabilities = total_current_liabilities + total_lt_debt + other_lt_liab

        # Equity
        # Original acquirer equity + value of stock issued (if any)
        stock_issued_value = self.deal.equity_purchase_price * (1 - self.deal.cash_percentage)
        total_equity = acq_bs.total_equity + stock_issued_value

        return {
            "assets": {
                "cash_and_equivalents": combined_cash,
                "accounts_receivable": accounts_receivable,
                "inventory": inventory,
                "other_current_assets": other_current,
                "total_current_assets": total_current_assets,
                "property_plant_equipment": ppe,
                "goodwill": total_goodwill,
                "new_goodwill_created": new_goodwill,
                "intangible_assets": total_intangibles,
                "new_intangibles_created": identifiable_intangibles,
                "other_non_current_assets": other_non_current,
                "total_assets": total_assets,
            },
            "liabilities": {
                "accounts_payable": accounts_payable,
                "short_term_debt": short_term_debt,
                "other_current_liabilities": other_current_liab,
                "total_current_liabilities": total_current_liabilities,
                "long_term_debt": total_lt_debt,
                "new_debt_raised": new_debt,
                "other_non_current_liabilities": other_lt_liab,
                "total_liabilities": total_liabilities,
            },
            "equity": {
                "total_equity": total_equity,
                "stock_consideration_added": stock_issued_value,
            },
            "check": {
                "total_liabilities_and_equity": total_liabilities + total_equity,
                "balanced": abs(total_assets - (total_liabilities + total_equity)) < 1,
            }
        }

    def generate_cash_flow_projection(self, year: int) -> Dict:
        """Generate cash flow projection for a given year."""
        income_stmt = self.generate_combined_income_statement(year)

        # Operating cash flow
        net_income = income_stmt["net_income"]
        da = income_stmt["depreciation_amortization"]
        revenue = income_stmt["combined_revenue"]

        # Working capital change (simplified)
        prev_income = self.generate_combined_income_statement(year - 1) if year > 1 else self.generate_combined_income_statement(0)
        revenue_change = revenue - prev_income["combined_revenue"]
        nwc_change = revenue_change * self.assumptions.nwc_percent_revenue

        operating_cf = net_income + da - nwc_change

        # Investing activities
        capex = revenue * self.assumptions.capex_percent_revenue

        # Free cash flow
        fcf = operating_cf - capex

        # Financing activities (debt paydown)
        debt_paydown = fcf * self.assumptions.debt_paydown_percent_fcf if fcf > 0 else 0

        return {
            "year": year,
            "net_income": net_income,
            "depreciation_amortization": da,
            "working_capital_change": -nwc_change,
            "operating_cash_flow": operating_cf,
            "capex": -capex,
            "free_cash_flow": fcf,
            "debt_paydown": -debt_paydown,
            "net_change_in_cash": fcf - debt_paydown,
        }

    def generate_credit_metrics(self, year: int) -> Dict:
        """Generate credit metrics for a given year."""
        income_stmt = self.generate_combined_income_statement(year)
        balance_sheet = self.generate_combined_balance_sheet()  # At close, then project

        ebitda = income_stmt["combined_ebitda"]
        interest = income_stmt["interest_expense"]

        # Debt (simplified - at close)
        total_debt = (
            balance_sheet["liabilities"]["short_term_debt"] +
            balance_sheet["liabilities"]["long_term_debt"]
        )

        # Adjust for debt paydown in projection years
        if year > 0:
            cumulative_paydown = 0
            for y in range(1, year + 1):
                cf = self.generate_cash_flow_projection(y)
                cumulative_paydown += abs(cf.get("debt_paydown", 0))
            total_debt = max(0, total_debt - cumulative_paydown)

        return {
            "year": year,
            "total_debt": total_debt,
            "ebitda": ebitda,
            "interest_expense": interest,
            "leverage_ratio": total_debt / ebitda if ebitda > 0 else float('inf'),
            "interest_coverage": ebitda / interest if interest > 0 else float('inf'),
            "debt_to_equity": total_debt / balance_sheet["equity"]["total_equity"],
        }

    def generate_full_projection(self) -> Dict:
        """Generate full multi-year pro forma projection."""
        years = self.assumptions.projection_years

        income_statements = {}
        cash_flows = {}
        credit_metrics = {}

        for year in range(years + 1):  # Include year 0 (close)
            income_statements[f"year_{year}"] = self.generate_combined_income_statement(year)
            if year > 0:
                cash_flows[f"year_{year}"] = self.generate_cash_flow_projection(year)
            credit_metrics[f"year_{year}"] = self.generate_credit_metrics(year)

        return {
            "balance_sheet_at_close": self.generate_combined_balance_sheet(),
            "income_statements": income_statements,
            "cash_flows": cash_flows,
            "credit_metrics": credit_metrics,
            "assumptions": {
                "projection_years": self.assumptions.projection_years,
                "acquirer_revenue_growth": self.assumptions.acquirer_revenue_growth,
                "target_revenue_growth": self.assumptions.target_revenue_growth,
                "tax_rate": self.assumptions.tax_rate,
            }
        }

    def get_key_metrics_summary(self) -> Dict:
        """Get summary of key pro forma metrics."""
        close = self.generate_combined_income_statement(0)
        year1 = self.generate_combined_income_statement(1)
        year5 = self.generate_combined_income_statement(5)

        credit_close = self.generate_credit_metrics(0)
        credit_year5 = self.generate_credit_metrics(5)

        return {
            "revenue": {
                "at_close": close["combined_revenue"],
                "year_1": year1["combined_revenue"],
                "year_5": year5["combined_revenue"],
                "cagr_5yr": (year5["combined_revenue"] / close["combined_revenue"]) ** (1/5) - 1,
            },
            "ebitda": {
                "at_close": close["combined_ebitda"],
                "year_1": year1["combined_ebitda"],
                "year_5": year5["combined_ebitda"],
            },
            "net_income": {
                "at_close": close["net_income"],
                "year_1": year1["net_income"],
                "year_5": year5["net_income"],
            },
            "margins": {
                "ebitda_margin_close": close["ebitda_margin"],
                "ebitda_margin_year5": year5["ebitda_margin"],
                "net_margin_close": close["net_income_margin"],
                "net_margin_year5": year5["net_income_margin"],
            },
            "leverage": {
                "at_close": credit_close["leverage_ratio"],
                "year_5": credit_year5["leverage_ratio"],
                "deleveraging": credit_close["leverage_ratio"] - credit_year5["leverage_ratio"],
            },
            "coverage": {
                "at_close": credit_close["interest_coverage"],
                "year_5": credit_year5["interest_coverage"],
            }
        }
