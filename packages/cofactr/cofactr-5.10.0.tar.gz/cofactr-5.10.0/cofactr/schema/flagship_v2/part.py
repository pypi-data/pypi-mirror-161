"""Part class."""
# Standard Modules
from dataclasses import dataclass
from typing import List

# Local Modules
from cofactr.kb.entity.types import PricePoint
from cofactr.schema.flagship.part import Part as FlagshipPart
from cofactr.schema.types import TerminationType


@dataclass
class Part(FlagshipPart):
    """Part."""

    buyable_reference_prices: List[PricePoint]
    reference_prices: List[PricePoint]
    termination_type: TerminationType
