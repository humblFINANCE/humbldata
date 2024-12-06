"""
Momentum Standard Model.

Context: Toolbox || Category: Technical || Command: momentum.

This module is used to define the QueryParams and Data model for the
Momentum command.
"""

from typing import Literal, TypeVar

import pandera.polars as pa
import polars as pl
from openbb import obb
from pydantic import Field, field_validator

from humbldata.core.standard_models.abstract.data import Data
from humbldata.core.standard_models.abstract.humblobject import HumblObject
from humbldata.core.standard_models.abstract.query_params import QueryParams
from humbldata.core.standard_models.toolbox import ToolboxQueryParams
from humbldata.core.utils.env import Env
from humbldata.core.utils.logger import log_start_end, setup_logger

env = Env()
Q = TypeVar("Q", bound=ToolboxQueryParams)
logger = setup_logger("MomentumFetcher", level=env.LOGGER_LEVEL)

MOMENTUM_QUERY_DESCRIPTIONS = {
    "method": "Method to calculate momentum (log, simple, or shift)",
    "period": "Number of periods to look back for momentum calculation",
}


class MomentumQueryParams(QueryParams):
    """
    QueryParams model for the Momentum command.

    Parameters
    ----------
    method : Literal["log", "simple", "shift"]
        Method to calculate momentum
    period : int
        Number of periods to look back
    """

    method: Literal["log", "simple", "shift"] = Field(
        default="log",
        title="Calculation Method",
        description=MOMENTUM_QUERY_DESCRIPTIONS["method"],
    )
    period: int = Field(
        default=1,
        title="Look-back Period",
        description=MOMENTUM_QUERY_DESCRIPTIONS["period"],
        ge=1,  # Must be greater than or equal to 1
    )

    @field_validator("method")
    @classmethod
    def validate_method(
        cls, v: Literal["log", "simple", "shift"]
    ) -> Literal["log", "simple", "shift"]:
        return v


class MomentumData(Data):
    """
    Data model for the momentum command, a Pandera.Polars Model.

    This Data model is used to validate data in the `.transform_data()` method of the `MomentumFetcher` class.
    """

    example_column: pl.Date = Field(
        default=None,
        title="Example Column",
        description="Description for example column",
    )


class MomentumFetcher:
    """
    Fetcher for the Momentum command.

    Parameters
    ----------
    context_params : ToolboxQueryParams
        The context parameters for the Toolbox query.
    command_params : MomentumQueryParams
        The command-specific parameters for the Momentum query.

    Attributes
    ----------
    context_params : ToolboxQueryParams
        Stores the context parameters passed during initialization.
    command_params : MomentumQueryParams
        Stores the command-specific parameters passed during initialization.
    data : pl.DataFrame
        The raw data extracted from the data provider, before transformation.
    warnings : List[Warning_]
        List of warnings generated during data processing.
    extra : dict
        Additional metadata or results from data processing.
    chart : Optional[Chart]
        Optional chart object for visualization.

    Methods
    -------
    transform_query()
        Transform the command-specific parameters into a query.
    extract_data()
        Extracts the data from the provider and returns it as a Polars DataFrame.
    transform_data()
        Transforms the command-specific data according to the Momentum logic.
    fetch_data()
        Execute TET Pattern.

    Returns
    -------
    HumblObject
        results : MomentumData
            Serializable results.
        provider : Literal['fmp', 'intrinio', 'polygon', 'tiingo', 'yfinance']
            Provider name.
        warnings : List[Warning_]
            List of warnings from both context and command.
        chart : Optional[Chart]
            Chart object.
        context_params : ToolboxQueryParams
            Context-specific parameters.
        command_params : MomentumQueryParams
            Command-specific parameters.
        extra : dict
            Additional metadata or results.
    """

    def __init__(
        self,
        context_params: ToolboxQueryParams,
        command_params: MomentumQueryParams,
    ):
        """
        Initialize the MomentumFetcher with context and command parameters.

        Parameters
        ----------
        context_params : ToolboxQueryParams
            The context parameters for the Toolbox query.
        command_params : MomentumQueryParams
            The command-specific parameters for the Momentum query.
        """
        self.context_params = context_params
        self.command_params = command_params
        self.warnings = []
        self.extra = {}
        self.chart = None

    def transform_query(self):
        """
        Transform the command-specific parameters into a query.

        If command_params is not provided, it initializes a default MomentumQueryParams object.
        """
        if not self.command_params:
            self.command_params = MomentumQueryParams()
        else:
            self.command_params = MomentumQueryParams(**self.command_params)

    def extract_data(self):
        """
        Extract the data from the provider and returns it as a Polars DataFrame.

        Returns
        -------
        pl.DataFrame
            The extracted data as a Polars DataFrame.
        """
        # Implement data extraction logic here
        self.equity_historical_data: pl.LazyFrame = (
            obb.equity.price.historical(
                symbol=self.context_params.symbols,
                start_date=self.context_params.start_date,
                end_date=self.context_params.end_date,
                provider=self.context_params.provider,
                # add kwargs
            )
            .to_polars()
            .lazy()
        )
        if len(self.context_params.symbols) == 1:
            self.equity_historical_data = (
                self.equity_historical_data.with_columns(
                    symbol=pl.lit(self.context_params.symbols[0])
                )
            )
        return self

    def transform_data(self):
        """
        Transform the command-specific data according to the momentum logic.

        Returns
        -------
        pl.DataFrame
            The transformed data as a Polars DataFrame
        """
        try:
            logger.debug("Transforming data with momentum calculation")

            # Add momentum calculation parameters to extra dict for metadata
            self.extra.update(
                {
                    "calculation_method": "log",  # Default method
                    "period": 1,  # Default period
                }
            )

            # Import momentum calculation
            from humbldata.toolbox.technical.momentum.model import momentum

            # Calculate momentum using the extracted data
            self.transformed_data = momentum(
                data=self.equity_historical_data,
                method=self.command_params.method,
                period=self.command_params.period,
            ).collect()

            # Validate the transformed data

            # self.transformed_data = schema(self.transformed_data) #TODO: add

            return self

        except Exception as e:
            logger.error(f"Failed to transform momentum data: {str(e)}")
            raise HumblDataError(
                f"Momentum transformation failed: {str(e)}"
            ) from e

    @log_start_end(logger=logger)
    def fetch_data(self):
        """
        Execute TET Pattern.

        This method executes the query transformation, data fetching and
        transformation process by first calling `transform_query` to prepare the query parameters, then
        extracting the raw data using `extract_data` method, and finally
        transforming the raw data using `transform_data` method.

        Returns
        -------
        HumblObject
            The HumblObject containing the transformed data and metadata.
        """
        logger.debug("Running .transform_query()")
        self.transform_query()
        logger.debug("Running .extract_data()")
        self.extract_data()
        logger.debug("Running .transform_data()")
        self.transform_data()

        # Initialize warnings list if it doesn't exist
        if not hasattr(self.context_params, "warnings"):
            self.context_params.warnings = []

        # Initialize fetcher warnings if they don't exist
        if not hasattr(self, "warnings"):
            self.warnings = []

        # Initialize extra dict if it doesn't exist
        if not hasattr(self, "extra"):
            self.extra = {}

        # Combine warnings from both sources
        all_warnings = self.context_params.warnings + self.warnings

        return HumblObject(
            results=self.transformed_data,
            provider=self.context_params.provider,
            warnings=all_warnings,  # Use combined warnings
            chart=self.chart,
            context_params=self.context_params,
            command_params=self.command_params,
            extra=self.extra,  # pipe in extra from transform_data()
        )
