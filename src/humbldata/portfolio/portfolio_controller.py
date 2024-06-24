"""
**Context: Portfolio**.

The portfolio Controller Module.
"""

from humbldata.core.standard_models.portfolio import portfolioQueryParams
from humbldata.portfolio.analytics.analytics_controller import Analytics


class Portfolio(portfolioQueryParams):
    """
    A top-level portfolio controller for data analysis tools in `humblDATA`.

    This module serves as the primary controller, routing user-specified
    portfolioQueryParams as core arguments that are used to fetch time series
    data.

    The `portfolio` controller also gives access to all sub-modules and their
    functions.

    It is designed to facilitate the collection of data across various types such as
    stocks, options, or alternative time series by requiring minimal input from the user.

    Submodules
    ----------
    The `Portfolio` controller is composed of the following submodules:

    - `analytics`:

    Parameters
    ----------
    # Add your analyticsQueryParams parameters here

    Parameter Notes
    -----
    The parameters are the `portfolioQueryParams`. They are used
    for data collection further down the pipeline in other commands.
    Intended to execute operations on core data sets. This approach enables
    composable and standardized querying while accommodating data-specific
    collection logic.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the Portfolio module.

        This method does not take any parameters and does not return anything.
        """
        super().__init__(*args, **kwargs)

    @property
    def analytics(self):
        """
        The analytics submodule of the Portfolio controller.

        Access to all the analytics indicators. When the portfolio class is
        instantiated the parameters are initialized with the portfolioQueryParams
        class, which hold all the fields needed for the context_params, like the
        symbol, interval, start_date, and end_date.
        """
        return Analytics(context_params=self)