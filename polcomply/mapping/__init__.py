"""
Mapping module for PolComply SDK

Licensed under the Business Source License 1.1 (BSL).
See LICENSE file for full terms.
"""

from .csv_to_fa import CSVToFAMapper, MappingError

__all__ = ["CSVToFAMapper", "MappingError"]
