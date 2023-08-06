import concurrent.futures
import datetime
import functools
import json
import pprint
from collections import OrderedDict
from typing import Any, List, NamedTuple, Optional, Union

import pandas as pd
from cachetools import TTLCache, cached
from pandas import DataFrame
from typeguard import typechecked

from gantry.api_client import APIClient
from gantry.exceptions import GantryException, QueryError
from gantry.query.core.constants import MAX_SIZE_CACHE_B, MAX_TTL_CACHE_SECS
from gantry.query.core.queryframe import GantryQueryFrame, QueryInfo
from gantry.query.core.utils import (
    check_response,
    get_application_node_id,
    get_application_views,
    get_last_application_version,
    get_start_end_time_from_view,
    runs_on,
)

MAX_WORKERS = 32  # Arbitrary workers for the 'describe' fetching op in dataframe


@cached(TTLCache(maxsize=MAX_SIZE_CACHE_B, ttl=MAX_TTL_CACHE_SECS))
def _raw_query_cached_request(api_client: APIClient, dumped_json_data: str):
    return api_client.request("POST", "/api/v1/aggregate/query", json=json.loads(dumped_json_data))


class GantryDataFrame(GantryQueryFrame):
    """
    Two-dimensional dict that supports querying Gantry data.
    """

    def __init__(
        self,
        api_client: APIClient,
        application: str,
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        version: Optional[Union[int, str]] = None,
        env: Optional[str] = None,
        filters: Optional[List[dict]] = None,
    ):
        """
        :meta private: This is to skip constructor in the docs
        """
        start_time, end_time = GantryQueryFrame.resolve_time_strings(start_time, end_time)
        application_node_id = get_application_node_id(
            api_client, application, start_time, end_time, version
        )
        super().__init__(
            api_client,
            QueryInfo(application_node_id, application, version, env, start_time, end_time),
        )
        self.filters = filters or []  # Holds raw dict filters to be used when fetching data
        self.series = self._build_series()

    @classmethod
    def from_view(
        cls,
        api_client: APIClient,
        application: str,
        view: str,
        version: Optional[Union[str, int]],
        environment: Optional[str],
    ):
        version = version or get_last_application_version(
            api_client=api_client, application=application
        )
        views = get_application_views(
            api_client=api_client, application=application, version=version, environment=environment
        )
        try:
            env_condition = lambda v: (environment is None) or (  # noqa
                v["tag_filters"]["env"] == environment
            )
            view_obj = [v for v in views if v["name"] == view and env_condition(v)][0]
        except IndexError:
            raise RuntimeError(f"View {view} not found")

        start_time, end_time = get_start_end_time_from_view(view_obj)

        return cls(
            api_client=api_client,
            application=application,
            start_time=start_time,
            end_time=end_time,
            version=version,
            env=view_obj["tag_filters"]["env"],
            filters=view_obj["data_filters"],
        )

    def _clone_with_extra_filters(self, filters: "Filters") -> "GantryDataFrame":
        """Private method to clone a dataframe and add additional filters

        This is used when:

            df2 = df1[series > 20]

        We cannot change the state of df1 (ENG-2653), so we generate
        a copy with the new filters
        """
        # Fail in case the provided filters was applied to another df
        for f in filters.filter_objs:
            if f.series.parent_dataframe is not self:
                raise ValueError(
                    "Filter was performed on a different dataframe that "
                    "the one trying to filter. This is not supported."
                )

        # Important to keep existing filters to support
        #    df2 = df1[df1["some-col"] > 20]
        #    df3 = df2[df2["some_col"] < 50]
        return GantryDataFrame(
            api_client=self.api_client,
            application=self.query_info.application,
            version=self.query_info.version,
            env=self.query_info.environment,
            start_time=self.query_info.start_time,
            end_time=self.query_info.end_time,
            filters=[*self.filters, *[f.filter_ for f in filters.filter_objs]],
        )

    def __getitem__(self, key: str) -> Optional[Any]:
        try:
            return self.__getattr__(key)
        except AttributeError:
            raise KeyError(f"{key} is not a valid column")

    def __getattr__(self, name: str) -> Optional[Any]:
        if isinstance(name, Filters):
            filters = name  # Rename for clarity
            return self._clone_with_extra_filters(filters)

        if name in self.series:
            return self.series.get(name)
        elif name == "dtypes":
            return self._dtypes
        elif hasattr(GantrySeries, name):
            return self._aggregation_factory(name)

        raise AttributeError(f"{name} is not a valid attribute")

    def __len__(self):
        return int(self._aggregation_factory("count")().max(axis=1).values[0])

    def __repr__(self) -> str:
        info = {
            "application": self.query_info.application,
            "from": repr(self.query_info.start_time),
            "to": repr(self.query_info.end_time),
            "series": list(self.series.keys()),
        }
        return pprint.pformat(info, sort_dicts=False)

    @property
    def dtypes(self) -> pd.Series:
        """Return the column types"""
        return pd.Series(self._dtypes).sort_index(ascending=True)

    def head(self, n: int = 5) -> pd.DataFrame:  # type: ignore
        """Fetch the top n entries

        Args:
            n (int, defaults to 5): Number of entries to fetch

        Returns:
            A pandas dataframe object.
        """
        return self._head(n=n, query_filters=self.filters)

    def tail(self, n: int = 5) -> pd.DataFrame:  # type: ignore
        """Fetch the last n entries

        Args:
            n (int, defaults to 5): Number of entries to fetch

        Returns:
            A pandas dataframe object.
        """
        return self._tail(n=n, query_filters=self.filters)

    def fetch(self) -> pd.DataFrame:  # type: ignore
        """Fetch all entries

        Returns:
            A pandas dataframe object.
        """
        return self._fetch(query_filters=self.filters)

    def _aggregation_factory(self, aggregration: str):
        """Generates methods that calculate aggregations on the series
        that compose this dataframe."""

        def apply_aggr(*args, **kw):
            """Will call & display self.series.aggregation() for each series"""
            result = {}
            is_df_output = False
            for k, s in self.series.items():
                data = getattr(s, aggregration)()
                result[k] = data
                if isinstance(data, pd.DataFrame):
                    is_df_output = True

            if not is_df_output:
                result = DataFrame([list(result.values())], columns=list(result.keys()))

            return result

        return apply_aggr

    def _build_series(self) -> OrderedDict:
        ret = OrderedDict()

        for schema_type in ["prediction_datanodes", "feedback_datanodes", "projection_datanodes"]:
            for feature in self.metadata.get(schema_type, []):  # type: ignore
                ret[feature["name"]] = GantrySeries(
                    feature["name"],
                    feature["id"],
                    feature["dtype"],
                    feature["event_type"],
                    self,
                )

        return ret

    def describe(self) -> pd.DataFrame:
        """Print basic stats on the dataframe."""
        table = OrderedDict()  # type: ignore
        # Fetch all stats for series concurrently:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_series = OrderedDict()
            for name, s in self.series.items():
                future_to_series[executor.submit(s._describe)] = name
                table[name] = None  # hack to keep table, futures can be solved any order
            for future in concurrent.futures.as_completed(future_to_series):
                table[future_to_series[future]] = future.result()

        headers = list(table.keys())

        # Get a set of stats maintaining order
        x = [stat_name for series, stats in table.items() for stat_name, _ in stats.items()]
        all_stats = sorted(set(x), key=x.index)

        data = [
            [self.query_info.application] * len(headers),
            [self.query_info.start_time] * len(headers),
            [self.query_info.end_time] * len(headers),
        ]

        for stat in all_stats:
            row = [table[series].get(stat, "N/A") for series in headers]
            data.append(row)

        return pd.DataFrame(data, index=["application", "from", "to", *all_stats], columns=headers)


class _FilterObj(NamedTuple):
    """Private container of a raw dict filter and the series
    it applies to.
    """

    filter_: dict
    series: "GantrySeries"


class Filters:
    """Wrapper over a list of filter objects. This object will be used
    as return type when doing 'series > 10' with support for later
    indexing on dataframes or series
    """

    def __init__(self, filter_objs: List[_FilterObj]) -> None:
        self.filter_objs: List[_FilterObj] = filter_objs

    @classmethod
    def _from_single_filter(cls, filter_: dict, series: "GantrySeries") -> "Filters":
        return cls([_FilterObj(filter_, series)])

    def __and__(self, other: "Filters") -> "Filters":
        """Support chaining filters from same dataframe.
        Different series from same dataframes can be &-chained

        """
        parent_df = self.filter_objs[0].series.parent_dataframe

        for f in other.filter_objs:
            if f.series.parent_dataframe != parent_df:
                # Fail in case chaining of filters from different
                # dataframes.
                raise ValueError("Cannot &-compare series from different dataframes")

        return Filters([*self.filter_objs, *other.filter_objs])


SeriesFilterType = Optional[Union[float, int, str, bool, datetime.datetime]]
SortableType = Union[float, int, datetime.datetime]


def customseriestypechecker(func):
    @functools.wraps(func)
    def wrapper(self, other):
        if isinstance(other, GantrySeries):
            raise TypeError(
                "Series cannot be compared to each other directly, but multiple "
                "filters can be chained together using &, for example: "
                "gdf[(gdf[feat_1] != x) & (gdf[feat2] != y)]"
            )

        return func(self, other)

    return wrapper


class GantrySeries(GantryQueryFrame):
    """
    Gantry Series object, similar to Pandas Series.

    Operations on Gantry Series return objects that can be used as masks for
    Gantry Series or Gantry Dataframes.

    .. code-block:: python

       # Operations on series return masks
       mask = some_series.contains("apples")
       apples_series = some_series[mask]

       apples_series.fetch()


    """

    def __init__(
        self,
        name: str,
        id: str,
        datatype: str,
        series_type: str,
        parent_dataframe: GantryDataFrame,
    ) -> None:
        """
        :meta private: This is to skip constructor in the docs
        """
        super().__init__(parent_dataframe.api_client, parent_dataframe.query_info)
        self.name = name
        self.id = id
        self.datatype = datatype
        self.series_type = series_type
        self.parent_dataframe = parent_dataframe

    @property
    def filters(self) -> List[dict]:
        return self.parent_dataframe.filters

    def __getitem__(self, key: Any) -> Optional[Any]:
        if isinstance(key, Filters):
            df = self.parent_dataframe._clone_with_extra_filters(key)
            return df[self.name]

        raise ValueError(
            "GantrySeries object only supports filter masks "
            f"(for example 'series[series > 10]'). {key} is not a valid filter"
        )

    def _filter_builder(self, filter_type: str, value: Any) -> Filters:
        new_filter = {"feature_name": self.name, filter_type: value}
        return Filters._from_single_filter(new_filter, self)

    @runs_on("bool")
    def __invert__(self):
        return self._filter_builder("boolean_query", False)

    @customseriestypechecker
    @typechecked
    def __eq__(self, other: SeriesFilterType):  # type: ignore
        if other is None:
            raise ValueError("use is_none instead of == to check if something is None")
        elif self.dtype == "bool":
            return self._filter_builder("boolean_query", other)
        elif self.dtype in ["str", "uuid"]:
            return self._filter_builder("string_query", other)
        elif self.dtype in ["int", "float"]:
            return self._filter_builder("equals", other)
        else:
            raise ValueError(f"Currently cannot compare {self.dtype} to {other}.")

    @customseriestypechecker
    @typechecked
    def __ne__(self, other: SeriesFilterType):  # type: ignore
        if other is None:
            raise ValueError("use is_none instead of != to check if something is None")
        elif self.dtype == "bool":
            return self._filter_builder("boolean_query", not other)
        elif self.dtype in ["str", "uuid"]:
            return self._filter_builder("string_query", "^(?!({})$).*$".format(other))
        elif self.dtype in ["int", "float"]:
            return self._filter_builder("not_number_query", other)
        else:
            raise ValueError(f"Currently cannot compare {self.type} to {other}.")

    @runs_on("int", "float", "datetime")
    @customseriestypechecker
    @typechecked
    def __gt__(self, other: SortableType):
        return self._filter_builder("lower_bound", other)

    @runs_on("int", "float", "datetime")
    @customseriestypechecker
    @typechecked
    def __ge__(self, other: SortableType):
        return self._filter_builder("inclusive_lower_bound", other)

    @runs_on("int", "float", "datetime")
    @customseriestypechecker
    @typechecked
    def __lt__(self, other: SortableType):
        return self._filter_builder("upper_bound", other)

    @runs_on("int", "float", "datetime")
    @customseriestypechecker
    @typechecked
    def __le__(self, other: SortableType):
        return self._filter_builder("inclusive_upper_bound", other)

    def __len__(self):
        return self.count()

    @runs_on("str")
    @typechecked
    def isin(self, other: List[str]):
        """For string Series, whether an entry is in a list of strings.

        Args:
            other (list[str]): the list of strings

        """
        return self._filter_builder("category_query", other)

    @runs_on("str")
    @typechecked
    def contains(self, other: str):
        """For string Series, whether an entry contains a string

        Args:
            other (str): string to compare

        """
        return self._filter_builder("string_query", other)

    def notnull(self):
        """Filters out null values."""
        return self._filter_builder("null_value", False)

    def notna(self):
        """Alias for notnull"""
        return self.notnull()

    def isnull(self):
        """Filters out non null values (ie, null values remain)"""
        return self._filter_builder("null_value", True)

    def isna(self):
        """Alias for isnull"""
        return self.isnull()

    def __repr__(self) -> str:
        info = {
            "application": self.parent_dataframe.query_info.application,
            "from": repr(self.query_info.start_time),
            "to": repr(self.query_info.end_time),
            "name": self.name,
            "type": self.dtype,
            "series_type": self.series_type,
        }
        return pprint.pformat(info, sort_dicts=False)

    def __getattr__(self, name: str):
        if name == "dtype":
            return self._dtype()

    def _get_dtype(self, column_name: str) -> str:
        return self.parent_dataframe._dtypes.get(column_name)

    def head(self, n: int = 5) -> pd.DataFrame:  # type: ignore
        """Fetch the top n entries

        Args:
            n (int, defaults to 5): Number of entries to fetch

        Returns:
            A pandas dataframe object.
        """
        return self._head(n=n, column=self.name, query_filters=self.parent_dataframe.filters)

    def tail(self, n: int = 5) -> pd.DataFrame:  # type: ignore
        """Fetch the last n entries

        Args:
            n (int, defaults to 5): Number of entries to fetch

        Returns:
            A pandas dataframe object.
        """
        return self._tail(n=n, column=self.name, query_filters=self.parent_dataframe.filters)

    def fetch(self) -> pd.DataFrame:  # type: ignore
        """Fetch all entries

        Returns:
            A pandas dataframe object.
        """
        return self._fetch(column=self.name, query_filters=self.parent_dataframe.filters)

    @runs_on("int", "float")
    def mean(self) -> float:
        """
        Runs on numeric series only.
        Get the computed average of this GantrySeries, if available

        Returns:
            float mean
        """
        try:
            return self._aggregate_query("mean")
        except (AttributeError, ValueError, KeyError):
            raise QueryError("Invalid query. GantrySeries cannot determine mean")

    @runs_on("int", "float")
    def std(self) -> float:
        """
        Runs on numeric series only.
        Get the standard deviation for this GantrySeries, if available

        Returns:
            float standard deviation
        """
        try:
            return self._aggregate_query("stddev")
        except (AttributeError, ValueError, KeyError):
            raise QueryError("Invalid query. GantrySeries cannot determine standard deviation")

    @runs_on("int", "float")
    def median(self) -> float:
        """
        Runs on numeric series only.
        Get the median for this GantrySeries, if available

        Returns:
            float median
        """
        try:
            quantiles = self.quantile([0.5])
            return quantiles[0.5]
        except (AttributeError, ValueError, KeyError):
            raise QueryError("Invalid query. GantrySeries cannot determine median")

    def count(self) -> int:
        """
        Get the number of available data points for this GantrySeries, if available.

        Returns:
            int total count
        """
        try:
            return self._aggregate_query("total")
        except (AttributeError, ValueError, KeyError):
            raise QueryError("Invalid query. GantrySeries cannot determine count")

    @runs_on("int", "float", "datetime")
    def min(self):
        """
        Runs on numeric and datetime series only.
        Get the minimum for this GantrySeries, if available.
        """
        try:
            return self._aggregate_query("minimum")
        except (AttributeError, ValueError, KeyError):
            raise QueryError("Invalid query. GantrySeries cannot determine min")

    @runs_on("int", "float", "datetime")
    def max(self):
        """
        Runs on numeric and datetime series only.
        Get the maximum for this GantrySeries, if available.
        """
        try:
            return self._aggregate_query("maximum")
        except (AttributeError, ValueError, KeyError):
            raise QueryError("Invalid query. GantrySeries cannot determine max")

    def histogram(self):
        """
        Get histogram of categories for this GantrySeries, if available.

        Gets the histogram of percentages from [0, 1] for available data values
        for this GantrySeries.

        Returns:
            Dict[str, float] histogram
        """
        try:
            hist_res = self._aggregate_query("category_percents")
            return hist_res
        except (AttributeError, ValueError, KeyError):
            raise QueryError("Invalid query. GantrySeries cannot determine histogram")

    @runs_on("int", "float")
    def quantile(self, quantile_vals: List[float] = [0.5]):
        """
        Get quantiles for this GantrySeries, if available.

        Args:
            quantile_vals: list of requested quantiles. Float values in the list should be in the
                range [0, 1].
        Returns:
            List[floats] of len(quantiles_vals) where the order of the outputs matches the input
                quantile_vals order.
        """
        try:
            quantile_res = self._aggregate_query("quantiles", {"quantile_vals": quantile_vals})
            return {float(k): v for k, v in quantile_res.items()}
        except (AttributeError, ValueError, KeyError):
            raise QueryError("Invalid query. GantrySeries cannot determine quantiles")

    def pdf(self):
        """
        Get requested probability density function for this GantrySeries, if available.
        """
        try:
            pdf_res = self._aggregate_query("pdf")
            return pd.DataFrame(pdf_res)
        except (AttributeError, ValueError, KeyError):
            raise QueryError("Invalid query. GantrySeries cannot determine pdf")

    def cdf(self):
        """
        Get requested cumulative density function for this GantrySeries, if available.
        """
        try:
            cdf_res = self._aggregate_query("cdf")
            return pd.DataFrame(cdf_res)
        except (AttributeError, ValueError, KeyError):
            raise QueryError("Invalid query. GantrySeries cannot determine cdf")

    def _dtype(self):
        return self.datatype

    def _aggregate_query(self, attribute, attribute_kwargs={}):
        data = self.query_info.get_base_query_params()
        data["queries"] = {
            "query": {
                "query_type": "feature",
                "model_node_id": self.query_info.application_node_id,
                "stat": attribute,
                "stat_kwargs": {attribute: attribute_kwargs},
                "feature": self.name,
                "filters": self.parent_dataframe.filters,
            }
        }
        response = _raw_query_cached_request(
            self.api_client, json.dumps(data, default=lambda x: x.isoformat())
        )
        try:
            check_response(response)
            return response["data"]["query"][attribute]
        except GantryException as e:
            raise GantryException(
                "Aggregation query [" + attribute + "] failed on API with this error: " + str(e)
            )

    def _describe(self) -> dict:
        c = self.count()
        table = {
            "series type": self.series_type,
            "type": self.dtype,
            "count": c,
            "not null count": self[self.notnull()].count(),  # type: ignore
            "null count": self[self.isnull()].count(),  # type: ignore
        }
        if self.dtype in ["int", "float", "datetime"]:
            table.update(
                {
                    "mean": self.mean(),
                    "min": self.min(),
                    "max": self.max(),
                }
            )
        if self.dtype in ["int", "float"]:
            q = self.quantile([0.25, 0.5, 0.75])
            table.update(
                {
                    "q25": q[0.25],
                    "q50": q[0.5],
                    "q75": q[0.75],
                }
            )
        if self.dtype == "bool":
            table["True rate"] = self[self == True].count() / c  # type: ignore # noqa

        return table

    def describe(self) -> pd.DataFrame:
        """Return basic stats on the series.

        Returns:
            A pandas dataframe with summary information.

        """
        stats = self._describe()
        return pd.DataFrame(
            [
                self.parent_dataframe.query_info.application,
                self.parent_dataframe.query_info.start_time,
                self.parent_dataframe.query_info.end_time,
                *stats.values(),
            ],
            index=["application", "from", "to", *stats.keys()],
            columns=[self.name],
        )
