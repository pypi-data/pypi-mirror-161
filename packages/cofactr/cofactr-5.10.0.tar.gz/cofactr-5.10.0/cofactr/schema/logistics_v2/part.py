"""Part class."""
# Standard Modules
from dataclasses import dataclass

# Local Modules
from cofactr.schema.logistics.part import Part as LogisticsPart
from cofactr.schema.types import TerminationType


@dataclass
class Part(LogisticsPart):
    """Part."""

    termination_type: TerminationType
