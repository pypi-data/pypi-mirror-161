"""Part class."""
# Standard Modules
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional

# Local Modules
from cofactr.schema.types import Document, TerminationType


@dataclass
class Part:  # pylint: disable=too-many-instance-attributes
    """Part."""

    id: str
    deprecated_ids: List[str]

    classification: Optional[str]
    description: Optional[str]
    documents: List[Document]
    hero_image: Optional[str]
    mpn: Optional[str]
    mfr: Optional[str]
    msl: Optional[str]
    package: Optional[str]
    specs: List[Dict[Literal["id", "label", "value"], str]]
    terminations: Optional[int]
    termination_type: TerminationType

    updated_at: Optional[str]

    def __post_init__(self):
        """Post initialization."""

        self.mfg = self.mfr
