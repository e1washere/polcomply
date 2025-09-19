"""
PolComply SDK - Polish KSeF compliance toolkit

Licensed under the Business Source License 1.1 (BSL).
See LICENSE file for full terms.
"""

__version__ = "0.1.0"
__author__ = "e1washere"
__email__ = "e1washere@example.com"

try:
    from .mapping.csv_to_fa import CSVToFAMapper, MappingError
    from .validators.xsd import ValidationError, XSDValidator
except ImportError:
    # Fallback for direct execution
    CSVToFAMapper = None
    MappingError = None
    ValidationError = None
    XSDValidator = None

__all__ = ["XSDValidator", "ValidationError", "CSVToFAMapper", "MappingError"]
