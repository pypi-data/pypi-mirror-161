"""Schema definitions."""
# Standard Modules
from enum import Enum
from typing import Callable, Dict

# Local Modules
from cofactr.helpers import identity
from cofactr.schema.flagship.offer import Offer as FlagshipOffer
from cofactr.schema.logistics.offer import Offer as LogisticsOffer
from cofactr.schema.flagship.part import Part as FlagshipPart
from cofactr.schema.flagship_v2.part import Part as FlagshipV2Part
from cofactr.schema.flagship_v3.part import Part as FlagshipV3Part
from cofactr.schema.logistics.part import Part as LogisticsPart
from cofactr.schema.logistics_v2.part import Part as LogisticsV2Part
from cofactr.schema.logistics_v3.part import Part as LogisticsV3Part
from cofactr.schema.logistics_v4.part import Part as LogisticsV4Part
from cofactr.schema.flagship.seller import Seller as FlagshipSeller
from cofactr.schema.price_solver_v0.part import Part as PriceSolverV0Part


class ProductSchemaName(str, Enum):
    """Product schema name."""

    INTERNAL = "internal"
    FLAGSHIP = "flagship"
    FLAGSHIP_V2 = "flagship-v2"
    FLAGSHIP_V3 = "flagship-v3"
    LOGISTICS = "logistics"
    LOGISTICS_V2 = "logistics-v2"
    LOGISTICS_V3 = "logistics-v3"
    LOGISTICS_V4 = "logistics-v4"
    PRICE_SOLVER_V0 = "price-solver-v0"


schema_to_product: Dict[ProductSchemaName, Callable] = {
    ProductSchemaName.INTERNAL: identity,
    ProductSchemaName.FLAGSHIP: FlagshipPart,
    ProductSchemaName.FLAGSHIP_V2: FlagshipV2Part,
    ProductSchemaName.FLAGSHIP_V3: FlagshipV3Part,
    ProductSchemaName.LOGISTICS: LogisticsPart,
    ProductSchemaName.LOGISTICS_V2: LogisticsV2Part,
    ProductSchemaName.LOGISTICS_V3: LogisticsV3Part,
    ProductSchemaName.LOGISTICS_V4: LogisticsV4Part,
    ProductSchemaName.PRICE_SOLVER_V0: PriceSolverV0Part,
}


class OfferSchemaName(str, Enum):
    """Offer schema name."""

    INTERNAL = "internal"
    FLAGSHIP = "flagship"
    LOGISTICS = "logistics"


schema_to_offer: Dict[OfferSchemaName, Callable] = {
    OfferSchemaName.INTERNAL: identity,
    OfferSchemaName.FLAGSHIP: FlagshipOffer,
    OfferSchemaName.LOGISTICS: LogisticsOffer,
}


class OrgSchemaName(str, Enum):
    """Organization schema name."""

    INTERNAL = "internal"
    FLAGSHIP = "flagship"
    LOGISTICS = "logistics"


schema_to_org: Dict[OrgSchemaName, Callable] = {
    OrgSchemaName.INTERNAL: identity,
    OrgSchemaName.FLAGSHIP: FlagshipSeller,
    OrgSchemaName.LOGISTICS: FlagshipSeller,
}


class SupplierSchemaName(str, Enum):
    """Supplier schema name."""

    INTERNAL = "internal"
    FLAGSHIP = "flagship"
    LOGISTICS = "logistics"


schema_to_supplier: Dict[SupplierSchemaName, Callable] = {
    SupplierSchemaName.INTERNAL: identity,
    SupplierSchemaName.FLAGSHIP: FlagshipSeller,
    SupplierSchemaName.LOGISTICS: FlagshipSeller,
}
