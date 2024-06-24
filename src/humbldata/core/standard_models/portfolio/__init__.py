"""
Context: Portfolio || **Category: Analytics**.

This module defines the QueryParams and Data classes for the Portfolio context.
"""

from pydantic import Field, field_validator

from humbldata.core.standard_models.abstract.data import Data
from humbldata.core.standard_models.abstract.query_params import QueryParams
from humbldata.core.utils.constants import OBB_EQUITY_PRICE_HISTORICAL_PROVIDERS
from humbldata.core.utils.descriptions import QUERY_DESCRIPTIONS


class PortfolioQueryParams(QueryParams):
    """
    Query parameters for the PortfolioController.

    This class defines the query parameters used by the PortfolioController.

    Parameters
    ----------
    example_field1 : str
        An example field.
    example_field2 : int | None
        Another example field.
    """

    symbol: str | list[str] = Field(
        default="AAPL",
        title="Symbol",
        description=QUERY_DESCRIPTIONS.get("symbol", ""),
    )
    provider: OBB_EQUITY_PRICE_HISTORICAL_PROVIDERS = Field(
        default="yahoo",
        title="Provider",
        description=QUERY_DESCRIPTIONS.get("provider", ""),
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: str | list[str] | set[str]) -> str | list[str]:
        """
        Convert the stock symbol to uppercase.

        Parameters
        ----------
        v : Union[str, List[str], Set[str]]
            The stock symbol or collection of symbols to be converted.

        Returns
        -------
        Union[str, List[str]]
            The uppercase stock symbol or a comma-separated string of uppercase
            symbols.
        """
        # If v is a string, split it by commas into a list. Otherwise, ensure it's a list.
        v = v.split(",") if isinstance(v, str) else v

        # Trim whitespace and check if all elements in the list are strings
        if not all(isinstance(item.strip(), str) for item in v):
            msg = "Every element in `symbol` list must be a `str`"
            raise ValueError(msg)

        # Convert all elements to uppercase, trim whitespace, and join them with a comma
        return [symbol.strip().upper() for symbol in v]


class PortfolioData(Data):
    """
    The Data for the PortfolioController.
    """

    # Add your data model fields here
    pass
