"""Part class."""
# Standard Modules
from dataclasses import dataclass
from typing import List, Optional

# Local Modules
from cofactr.schema.flagship_v2.part import Part as FlagshipV2Part


@dataclass
class Part(FlagshipV2Part):
    """Part."""

    deprecated_ids: List[str]
    min_lead: Optional[int]

    def __post_init__(self):
        """Post initialization."""

        self.mfg = self.mfr
