"""Cofactr graph API client."""
# pylint: disable=too-many-arguments
# Python Modules
import dataclasses
import json
from typing import Any, Dict, List, Literal, Optional
from h11 import Response

# 3rd Party Modules
import httpx

# Local Modules
from cofactr.schema import (
    OfferSchemaName,
    OrgSchemaName,
    ProductSchemaName,
    SupplierSchemaName,
    schema_to_offer,
    schema_to_org,
    schema_to_product,
    schema_to_supplier,
)
from cofactr.schema.types import Completion

Protocol = Literal["http", "https"]


drop_none_values = lambda d: {k: v for k, v in d.items() if v is not None}

BATCH_LIMIT = 500


def get_products(
    url,
    client_id,
    api_key,
    query,
    fields,
    before,
    after,
    limit,
    external,
    force_refresh,
    schema,
    filtering,
    timeout: Optional[int] = None,
) -> httpx.Response:
    """Get products."""

    res = httpx.get(
        f"{url}/products",
        headers=drop_none_values(
            {
                "X-CLIENT-ID": client_id,
                "X-API-KEY": api_key,
            }
        ),
        params=drop_none_values(
            {
                "q": query,
                "fields": fields,
                "before": before,
                "after": after,
                "limit": limit,
                "external": external,
                "force_refresh": force_refresh,
                "schema": schema,
                "filtering": json.dumps(filtering) if filtering else None,
            }
        ),
        timeout=timeout,
    )

    res.raise_for_status()

    return res


def get_orgs(
    url,
    client_id,
    api_key,
    query,
    before,
    after,
    limit,
    schema,
    timeout,
) -> Response:
    """Get orgs."""

    res = httpx.get(
        f"{url}/orgs",
        headers=drop_none_values(
            {
                "X-CLIENT-ID": client_id,
                "X-API-KEY": api_key,
            }
        ),
        params=drop_none_values(
            {
                "q": query,
                "before": before,
                "after": after,
                "limit": limit,
                "schema": schema,
            }
        ),
        timeout=timeout,
    )

    res.raise_for_status()

    return res


class GraphAPI:  # pylint: disable=too-many-instance-attributes
    """A client-side representation of the Cofactr graph API."""

    PROTOCOL: Protocol = "https"
    HOST = "graph.cofactr.com"

    def __init__(
        self,
        protocol: Optional[Protocol] = PROTOCOL,
        host: Optional[str] = HOST,
        default_product_schema: ProductSchemaName = ProductSchemaName.FLAGSHIP,
        default_org_schema: OrgSchemaName = OrgSchemaName.FLAGSHIP,
        default_offer_schema: OfferSchemaName = OfferSchemaName.FLAGSHIP,
        default_supplier_schema: SupplierSchemaName = SupplierSchemaName.FLAGSHIP,
        client_id: Optional[str] = None,
        api_key: Optional[str] = None,
    ):

        self.url = f"{protocol}://{host}"
        self.default_product_schema = default_product_schema
        self.default_org_schema = default_org_schema
        self.default_offer_schema = default_offer_schema
        self.default_supplier_schema = default_supplier_schema
        self.client_id = client_id
        self.api_key = api_key

    def check_health(self):
        """Check the operational status of the service."""

        res = httpx.get(self.url)

        res.raise_for_status()

        return res.json()

    def get_products(
        self,
        query: Optional[str] = None,
        fields: Optional[str] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        limit: Optional[int] = None,
        external: Optional[bool] = True,
        force_refresh: bool = False,
        schema: Optional[ProductSchemaName] = None,
        filtering: Optional[List[Dict]] = None,
        timeout: Optional[int] = None,
    ):
        """Get products.

        Args:
            query: Search query.
            fields: Used to filter properties that the response should contain. A field can be a
                concrete property like "mpn" or an abstract group of properties like "assembly".
                Example: `"id,aliases,labels,statements{spec,assembly},offers"`.
            before: Upper page boundry, expressed as a product ID.
            after: Lower page boundry, expressed as a product ID.
            limit: Restrict the results of the query to a particular number of documents.
            external: Whether to query external sources.
            force_refresh: Whether to force re-ingestion from external sources. Overrides
                `external`.
            schema: Response schema.
            filtering: Filter products.
                Example: `[{"field":"id","operator":"IN","value":["CCCQSA3G9SMR","CCV1F7A8UIYH"]}]`.
            timeout: Time to wait (in seconds) for the server to issue a response.
        """
        if not schema:
            schema = self.default_product_schema

        res = get_products(
            url=self.url,
            client_id=self.client_id,
            api_key=self.api_key,
            query=query,
            fields=fields,
            external=external,
            force_refresh=force_refresh,
            before=before,
            after=after,
            limit=limit,
            schema=schema.value,
            filtering=filtering,
            timeout=timeout,
        )

        extracted_producs = res.json()

        Product = schema_to_product[schema]  # pylint: disable=invalid-name

        extracted_producs["data"] = [
            Product(**data) for data in extracted_producs["data"]
        ]

        return extracted_producs

    def get_products_by_searches(
        self,
        queries: List[str],
        external: bool = True,
        force_refresh: bool = False,
        schema: Optional[ProductSchemaName] = None,
        timeout: Optional[int] = None,
    ):
        """Search for products associated with each query.

        Args:
            queries: Queries to find products for.
            external: Whether to query external sources in order to refresh data if applicable.
            force_refresh: Whether to force re-ingestion from external sources. Overrides
                `external`.
            schema: Response schema.
            timeout: Time to wait (in seconds) for the server to issue a response.

        Returns:
            A dictionary mapping each MPN to a list of matching products.
        """

        if not queries:
            return {}

        if not schema:
            schema = self.default_product_schema

        res = httpx.post(
            f"{self.url}/products",
            headers=drop_none_values(
                {
                    "X-CLIENT-ID": self.client_id,
                    "X-API-KEY": self.api_key,
                }
            ),
            json=[
                {
                    "method": "GET",
                    "relative_url": (
                        f"?q={query}&schema={schema.value}&external={bool(external)}"
                        f"&force_refresh={force_refresh}"
                    ),
                }
                for query in queries
            ],
            timeout=timeout,
        )

        res.raise_for_status()

        responses = res.json()

        Product = schema_to_product[schema]  # pylint: disable=invalid-name

        query_to_products: Dict[str, Any] = {}

        for query, response in zip(queries, responses):
            matches = []

            if response["code"] == 200:
                data = response["body"]["data"]

                matches = [Product(**product_data) for product_data in data]

            query_to_products[query] = matches

        return query_to_products

    def get_products_by_ids(
        self,
        ids: List[str],
        external: Optional[bool] = True,
        force_refresh: bool = False,
        schema: Optional[ProductSchemaName] = None,
        timeout: Optional[int] = None,
    ):
        """Get a batch of products.

        Note:
            A maximum of 500 IDs can be provided. Any more than that, and the server will return
            a 422 error. Consider breaking the request into batches.

        Args:
            ids: Cofactr product IDs to match on.
            external: Whether to query external sources in order to refresh data if applicable.
            force_refresh: Whether to force re-ingestion from external sources. Overrides
                `external`.
            schema: Response schema.
            timeout: Time to wait (in seconds) for the server to issue a response.
        """
        num_requested = len(ids)

        if num_requested > BATCH_LIMIT:
            raise ValueError(
                "Too many products requested in one call: Requested"
                f" {num_requested}, but the limit is {BATCH_LIMIT}."
            )

        if not schema:
            schema = self.default_product_schema

        extracted_products = self.get_products(
            external=external,
            force_refresh=force_refresh,
            schema=schema,
            filtering=[{"field": "id", "operator": "IN", "value": ids}],
            limit=BATCH_LIMIT,
            timeout=timeout,
        )

        id_to_product = {p.id: p for p in extracted_products["data"]}

        product_dataclass = schema_to_product[schema]

        if "deprecated_ids" in {
            field.name for field in dataclasses.fields(product_dataclass)
        }:
            for product in extracted_products["data"]:
                deprecated_ids = product.deprecated_ids

                for deprecated_id in deprecated_ids:
                    id_to_product[deprecated_id] = product

        products = {id_: id_to_product[id_] for id_ in ids if id_ in id_to_product}

        return products

    def get_orgs(
        self,
        query: Optional[str] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        limit: Optional[int] = None,
        schema: Optional[OrgSchemaName] = None,
        timeout: Optional[int] = None,
    ):
        """Get organizations.

        Args:
            query: Search query.
            before: Upper page boundry, expressed as a product ID.
            after: Lower page boundry, expressed as a product ID.
            limit: Restrict the results of the query to a particular number of documents.
            schema: Response schema.
            timeout: Time to wait (in seconds) for the server to issue a response.
        """
        if not schema:
            schema = self.default_org_schema

        res = get_orgs(
            url=self.url,
            client_id=self.client_id,
            api_key=self.api_key,
            query=query,
            before=before,
            after=after,
            limit=limit,
            schema=schema.value,
            timeout=timeout,
        )

        res_json = res.json()

        Org = schema_to_org[schema]  # pylint: disable=invalid-name

        res_json["data"] = [Org(**data) for data in res_json["data"]]

        return res_json

    def get_suppliers(
        self,
        query: Optional[str] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        limit: Optional[int] = None,
        schema: Optional[OrgSchemaName] = None,
        timeout: Optional[int] = None,
    ):
        """Get suppliers.

        Args:
            query: Search query.
            before: Upper page boundry, expressed as a product ID.
            after: Lower page boundry, expressed as a product ID.
            limit: Restrict the results of the query to a particular number of documents.
            schema: Response schema.
            timeout: Time to wait (in seconds) for the server to issue a response.
        """
        if not schema:
            schema = self.default_org_schema

        res = get_orgs(
            url=self.url,
            client_id=self.client_id,
            api_key=self.api_key,
            query=query,
            before=before,
            after=after,
            limit=limit,
            schema=schema.value,
            timeout=timeout,
        )

        res_json = res.json()

        Org = schema_to_org[schema]  # pylint: disable=invalid-name

        res_json["data"] = [Org(**data) for data in res_json["data"]]

        return res_json

    def autocomplete_orgs(
        self,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        types: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Dict[Literal["data"], Completion]:
        """Autocomplete organizations.

        Args:
            query: Search query.
            before: Upper page boundry, expressed as a product ID.
            after: Lower page boundry, expressed as a product ID.
            limit: Restrict the results of the query to a particular number of
                documents.
            types: Filter for types of organizations.
                Example: "supplier" filters to suppliers.
                Example: "supplier|manufacturer" filters to orgs that are a
                    supplier or a manufacturer.
            timeout: Time to wait (in seconds) for the server to issue a response.
        """

        res = httpx.get(
            f"{self.url}/orgs/autocomplete",
            headers=drop_none_values(
                {
                    "X-CLIENT-ID": self.client_id,
                    "X-API-KEY": self.api_key,
                }
            ),
            params=drop_none_values(
                {
                    "q": query,
                    "limit": limit,
                    "types": types,
                }
            ),
            timeout=timeout,
        )

        res.raise_for_status()

        return res.json()

    def get_product(
        self,
        id: str,
        fields: Optional[str] = None,
        external: Optional[bool] = True,
        force_refresh: bool = False,
        schema: Optional[ProductSchemaName] = None,
        timeout: Optional[int] = None,
    ):
        """Get product.

        Args:
            fields: Used to filter properties that the response should contain. A field can be a
                concrete property like "mpn" or an abstract group of properties like "assembly".
                Example: "id,aliases,labels,statements{spec,assembly},offers"
            external: Whether to query external sources in order to update information for the
                given product.
            force_refresh: Whether to force re-ingestion from external sources. Overrides
                `external`.
            schema: Response schema.
            timeout: Time to wait (in seconds) for the server to issue a response.
        """
        if not schema:
            schema = self.default_product_schema

        res = httpx.get(
            f"{self.url}/products/{id}",
            headers=drop_none_values(
                {
                    "X-CLIENT-ID": self.client_id,
                    "X-API-KEY": self.api_key,
                }
            ),
            params=drop_none_values(
                {
                    "fields": fields,
                    "external": external,
                    "force_refresh": force_refresh,
                    "schema": schema.value,
                }
            ),
            timeout=timeout,
        )

        res.raise_for_status()

        res_json = res.json()

        Product = schema_to_product[schema]  # pylint: disable=invalid-name

        res_json["data"] = (
            Product(**res_json["data"]) if (res_json and res_json.get("data")) else None
        )

        return res_json

    def get_offers(
        self,
        product_id: str,
        fields: Optional[str] = None,
        external: Optional[bool] = True,
        force_refresh: bool = False,
        schema: Optional[OfferSchemaName] = None,
        timeout: Optional[int] = None,
    ):
        """Get product.

        Args:
            product_id: ID of the product to get offers for.
            fields: Used to filter properties that the response should contain.
            external: Whether to query external sources in order to update information.
            force_refresh: Whether to force re-ingestion from external sources. Overrides
                `external`.
            schema: Response schema.
            timeout: Time to wait (in seconds) for the server to issue a response.
        """
        if not schema:
            schema = self.default_offer_schema

        res = httpx.get(
            f"{self.url}/products/{product_id}/offers",
            headers=drop_none_values(
                {
                    "X-CLIENT-ID": self.client_id,
                    "X-API-KEY": self.api_key,
                }
            ),
            params=drop_none_values(
                {
                    "fields": fields,
                    "external": external,
                    "force_refresh": force_refresh,
                    "schema": schema.value,
                }
            ),
            timeout=timeout,
        )

        res.raise_for_status()

        res_json = res.json()

        Offer = schema_to_offer[schema]  # pylint: disable=invalid-name

        res_json["data"] = [Offer(**data) for data in res_json["data"]]

        return res_json

    def get_org(
        self,
        id: str,
        schema: Optional[OrgSchemaName] = None,
        timeout: Optional[int] = None,
    ):
        """Get organization."""
        if not schema:
            schema = self.default_org_schema

        res = httpx.get(
            f"{self.url}/orgs/{id}",
            headers=drop_none_values(
                {
                    "X-CLIENT-ID": self.client_id,
                    "X-API-KEY": self.api_key,
                }
            ),
            params=drop_none_values({"schema": schema.value}),
            timeout=timeout,
        )

        res.raise_for_status()

        res_json = res.json()

        Org = schema_to_org[schema]  # pylint: disable=invalid-name

        res_json["data"] = (
            Org(**res_json["data"]) if (res_json and res_json.get("data")) else None
        )

        return res_json

    def get_supplier(
        self,
        id: str,
        schema: Optional[SupplierSchemaName] = None,
        timeout: Optional[int] = None,
    ):
        """Get supplier."""
        if not schema:
            schema = self.default_supplier_schema

        res = httpx.get(
            f"{self.url}/orgs/{id}",
            headers=drop_none_values(
                {
                    "X-CLIENT-ID": self.client_id,
                    "X-API-KEY": self.api_key,
                }
            ),
            params=drop_none_values({"schema": schema.value}),
            timeout=timeout,
        )

        res.raise_for_status()

        res_json = res.json()

        Supplier = schema_to_supplier[schema]  # pylint: disable=invalid-name

        res_json["data"] = (
            Supplier(**res_json["data"])
            if (res_json and res_json.get("data"))
            else None
        )

        return res_json
