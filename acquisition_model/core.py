"""
Core Acquisition Model - Main orchestration class for M&A analysis.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

from .company import Company, CompanyType, create_sample_acquirer, create_sample_target
from .deal_structure import DealStructure, create_sample_deal_structure
from .valuation import (
    ValuationAnalysis,
    DCFAssumptions,
    create_sample_trading_comps,
    create_sample_transaction_comps
)
from .synergies import SynergiesAnalysis, create_sample_synergies
from .eps_analysis import EPSAccretionDilution
from .pro_forma import ProFormaFinancials, ProFormaAssumptions
from .sensitivity import SensitivityAnalysis


class AcquisitionModel:
    """
    Main orchestration class for M&A acquisition analysis.

    This class ties together all components of the acquisition model:
    - Company data (acquirer and target)
    - Deal structure and financing
    - Valuation analysis (DCF, trading comps, transaction comps)
    - Synergies analysis
    - EPS accretion/dilution
    - Pro forma financials
    - Sensitivity analysis
    """

    def __init__(
        self,
        acquirer: Company,
        target: Company,
        deal_structure: DealStructure,
        synergies: Optional[SynergiesAnalysis] = None,
        model_name: str = "Acquisition Analysis"
    ):
        self.acquirer = acquirer
        self.target = target
        self.deal = deal_structure
        self.synergies = synergies
        self.model_name = model_name
        self.created_at = datetime.now()

        # Initialize analysis components
        self.valuation = ValuationAnalysis(target)
        self.eps_analysis = EPSAccretionDilution(acquirer, target, deal_structure, synergies)
        self.pro_forma = ProFormaFinancials(acquirer, target, deal_structure, synergies)
        self.sensitivity = SensitivityAnalysis(acquirer, target, deal_structure, synergies)

    # =========================================================================
    # Deal Summary Methods
    # =========================================================================

    def get_deal_summary(self) -> Dict:
        """Get high-level deal summary."""
        return {
            "model_name": self.model_name,
            "created_at": self.created_at.isoformat(),
            "acquirer": {
                "name": self.acquirer.name,
                "ticker": self.acquirer.ticker,
                "market_cap": self.acquirer.market_data.market_cap,
                "enterprise_value": self.acquirer.enterprise_value,
                "ltm_revenue": self.acquirer.income_statement.revenue,
                "ltm_ebitda": self.acquirer.income_statement.ebitda,
                "ltm_net_income": self.acquirer.income_statement.net_income,
            },
            "target": {
                "name": self.target.name,
                "ticker": self.target.ticker,
                "current_price": self.target.market_data.share_price,
                "market_cap": self.target.market_data.market_cap,
                "enterprise_value": self.target.enterprise_value,
                "ltm_revenue": self.target.income_statement.revenue,
                "ltm_ebitda": self.target.income_statement.ebitda,
                "ltm_net_income": self.target.income_statement.net_income,
            },
            "transaction": {
                "offer_price": self.deal.offer_price_per_share,
                "control_premium": self.deal.control_premium,
                "equity_value": self.deal.equity_purchase_price,
                "implied_ev": self.deal.implied_ev,
                "cash_percentage": self.deal.cash_percentage,
                "stock_percentage": 1 - self.deal.cash_percentage,
            },
            "multiples": {
                "ev_revenue": self.deal.implied_ev / self.target.income_statement.revenue,
                "ev_ebitda": self.deal.implied_ev / self.target.income_statement.ebitda,
                "pe_offer": self.deal.offer_price_per_share / self.target.eps,
            }
        }

    def get_sources_uses_summary(self) -> Dict:
        """Get sources and uses of funds summary."""
        return {
            "sources": self.deal.get_sources_of_funds(),
            "uses": self.deal.get_uses_of_funds(),
            "validation": self.deal.validate_sources_uses(),
        }

    # =========================================================================
    # Valuation Methods
    # =========================================================================

    def run_valuation_analysis(
        self,
        dcf_assumptions: Optional[DCFAssumptions] = None,
        include_comps: bool = True
    ) -> Dict:
        """Run comprehensive valuation analysis."""
        if dcf_assumptions:
            self.valuation.set_dcf_assumptions(dcf_assumptions)

        return self.valuation.get_valuation_summary(self.deal.offer_price_per_share)

    def get_football_field(self) -> Dict:
        """Get football field valuation summary."""
        return self.valuation.generate_football_field(self.deal.offer_price_per_share)

    # =========================================================================
    # Synergies Methods
    # =========================================================================

    def get_synergies_summary(self) -> Optional[Dict]:
        """Get synergies analysis summary."""
        if not self.synergies:
            return None
        return self.synergies.get_synergy_summary()

    # =========================================================================
    # EPS Analysis Methods
    # =========================================================================

    def run_eps_analysis(
        self,
        years: int = 5,
        include_synergies: bool = True
    ) -> Dict:
        """Run EPS accretion/dilution analysis."""
        return self.eps_analysis.get_analysis_summary()

    def get_eps_sensitivity(self) -> Dict:
        """Get EPS sensitivity to key variables."""
        return self.eps_analysis.sensitivity_analysis()

    # =========================================================================
    # Pro Forma Methods
    # =========================================================================

    def generate_pro_forma(self) -> Dict:
        """Generate full pro forma financial projections."""
        return self.pro_forma.generate_full_projection()

    def get_pro_forma_summary(self) -> Dict:
        """Get key pro forma metrics summary."""
        return self.pro_forma.get_key_metrics_summary()

    # =========================================================================
    # Sensitivity Analysis Methods
    # =========================================================================

    def run_sensitivity_analysis(self) -> Dict:
        """Run comprehensive sensitivity analysis."""
        return self.sensitivity.run_full_sensitivity_suite()

    def get_sensitivity_summary(self) -> Dict:
        """Get sensitivity analysis summary."""
        return self.sensitivity.get_sensitivity_summary()

    # =========================================================================
    # Full Model Output
    # =========================================================================

    def run_full_analysis(self) -> Dict:
        """Run complete acquisition analysis and return all results."""
        return {
            "summary": self.get_deal_summary(),
            "sources_uses": self.get_sources_uses_summary(),
            "valuation": self.run_valuation_analysis(),
            "synergies": self.get_synergies_summary(),
            "eps_analysis": self.run_eps_analysis(),
            "pro_forma": self.generate_pro_forma(),
            "sensitivity": self.get_sensitivity_summary(),
        }

    def generate_executive_summary(self) -> str:
        """Generate text executive summary of the deal."""
        deal = self.get_deal_summary()
        eps = self.eps_analysis.run_analysis(year=1, include_synergies=True)
        synergies = self.get_synergies_summary() if self.synergies else None

        lines = [
            f"=" * 80,
            f"ACQUISITION ANALYSIS: {deal['acquirer']['name']} / {deal['target']['name']}",
            f"=" * 80,
            "",
            "TRANSACTION OVERVIEW",
            "-" * 40,
            f"Acquirer: {deal['acquirer']['name']} ({deal['acquirer']['ticker']})",
            f"Target: {deal['target']['name']} ({deal['target']['ticker']})",
            f"",
            f"Offer Price: ${deal['transaction']['offer_price']:.2f} per share",
            f"Control Premium: {deal['transaction']['control_premium']:.1%}",
            f"Equity Value: ${deal['transaction']['equity_value'] / 1e9:.2f}B",
            f"Implied EV: ${deal['transaction']['implied_ev'] / 1e9:.2f}B",
            "",
            "DEAL STRUCTURE",
            "-" * 40,
            f"Cash Consideration: {deal['transaction']['cash_percentage']:.0%}",
            f"Stock Consideration: {deal['transaction']['stock_percentage']:.0%}",
            "",
            "VALUATION MULTIPLES",
            "-" * 40,
            f"EV/Revenue: {deal['multiples']['ev_revenue']:.2f}x",
            f"EV/EBITDA: {deal['multiples']['ev_ebitda']:.2f}x",
            f"P/E (on offer): {deal['multiples']['pe_offer']:.1f}x",
            "",
            "EPS IMPACT (Year 1)",
            "-" * 40,
            f"Acquirer Standalone EPS: ${eps['standalone']['acquirer_eps']:.2f}",
            f"Pro Forma EPS: ${eps['pro_forma']['eps']:.2f}",
            f"Accretion/(Dilution): {eps['accretion_dilution']['eps_change_percent']:.1%}",
            f"Result: {eps['accretion_dilution']['result'].upper()}",
        ]

        if synergies:
            lines.extend([
                "",
                "SYNERGIES (Run-Rate)",
                "-" * 40,
                f"Cost Synergies: ${synergies['total_run_rate_cost_synergies'] / 1e6:.0f}M",
                f"Revenue Synergies: ${synergies['total_run_rate_revenue_synergies'] / 1e6:.0f}M",
                f"EBITDA Impact: ${synergies['total_run_rate_ebitda_impact'] / 1e6:.0f}M",
                f"Integration Costs: ${synergies['total_integration_costs'] / 1e6:.0f}M",
                f"Years to Full Realization: {synergies['years_to_full_realization']}",
            ])

        lines.extend([
            "",
            "=" * 80,
        ])

        return "\n".join(lines)

    def export_to_json(self, filepath: str) -> None:
        """Export full analysis to JSON file."""
        results = self.run_full_analysis()

        # Convert non-serializable types
        def convert(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=convert)


def create_sample_model() -> AcquisitionModel:
    """Create a fully populated sample acquisition model for demonstration."""
    # Create companies
    acquirer = create_sample_acquirer()
    target = create_sample_target()

    # Create deal structure
    deal = create_sample_deal_structure(
        offer_price=75.0,
        target_shares=target.market_data.shares_outstanding,
        cash_pct=0.60
    )

    # Create synergies
    synergies = create_sample_synergies()

    # Create model
    model = AcquisitionModel(
        acquirer=acquirer,
        target=target,
        deal_structure=deal,
        synergies=synergies,
        model_name="TechCorp Industries / InnovateTech Solutions Acquisition"
    )

    # Add trading comps
    for comp in create_sample_trading_comps():
        model.valuation.add_trading_comp(comp)

    # Add transaction comps
    for comp in create_sample_transaction_comps():
        model.valuation.add_transaction_comp(comp)

    return model


def run_sample_analysis() -> None:
    """Run and print sample analysis."""
    model = create_sample_model()

    print(model.generate_executive_summary())
    print()

    # Print key metrics
    print("KEY PRO FORMA METRICS")
    print("-" * 40)
    metrics = model.get_pro_forma_summary()

    print(f"Combined Revenue (Close): ${metrics['revenue']['at_close'] / 1e9:.1f}B")
    print(f"Combined Revenue (Year 5): ${metrics['revenue']['year_5'] / 1e9:.1f}B")
    print(f"5-Year Revenue CAGR: {metrics['revenue']['cagr_5yr']:.1%}")
    print()
    print(f"Leverage at Close: {metrics['leverage']['at_close']:.2f}x")
    print(f"Leverage Year 5: {metrics['leverage']['year_5']:.2f}x")
    print(f"Deleveraging: {metrics['leverage']['deleveraging']:.2f}x")


if __name__ == "__main__":
    run_sample_analysis()
