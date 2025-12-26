"""
M&A Acquisition Analysis Model

A comprehensive financial model for analyzing merger and acquisition transactions,
including deal valuation, synergies analysis, EPS accretion/dilution, and pro forma financials.
"""

from .core import AcquisitionModel
from .valuation import ValuationAnalysis
from .synergies import SynergiesAnalysis
from .eps_analysis import EPSAccretionDilution
from .pro_forma import ProFormaFinancials
from .sensitivity import SensitivityAnalysis
from .deal_structure import DealStructure

__version__ = "1.0.0"
__all__ = [
    "AcquisitionModel",
    "ValuationAnalysis",
    "SynergiesAnalysis",
    "EPSAccretionDilution",
    "ProFormaFinancials",
    "SensitivityAnalysis",
    "DealStructure",
]
