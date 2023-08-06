"""Part class."""
# Standard Modules
from dataclasses import dataclass
from typing import List

# Local Modules
from cofactr.schema.flagship.offer import Offer as FlagshipOffer
from cofactr.schema.flagship_v3.part import Part as FlagshipV3Part


@dataclass
class Part(FlagshipV3Part):  # pylint: disable=too-many-instance-attributes
    """Part."""

    offers: List[FlagshipOffer]

    def __post_init__(self):
        """Post initialization."""

        self.mfg = self.mfr
        self.offers = [FlagshipOffer(**offer) for offer in self.offers]
