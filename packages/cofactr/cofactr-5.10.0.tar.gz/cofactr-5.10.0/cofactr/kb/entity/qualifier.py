"""Functions for constructing a KB entity."""
# Standard Modules
from typing import List

# Local Modules
from cofactr.kb.entity.types import Qualifier, Snak


def qualifier(
    property: str, snaks: List[Snak]  # pylint: disable=redefined-builtin
) -> Qualifier:
    """Qualifier."""

    return {
        property: snaks,
    }
