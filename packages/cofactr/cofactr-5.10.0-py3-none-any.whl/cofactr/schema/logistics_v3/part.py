"""Part class."""
# Standard Modules
from dataclasses import dataclass
from typing import List

# Local Modules
from cofactr.schema.logistics_v2.part import Part as LogisticsV2Part


@dataclass
class Part(LogisticsV2Part):
    """Part."""

    deprecated_ids: List[str]
