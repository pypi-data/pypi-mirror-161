try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore


import pandas as pd

from gantry.query import globals
from gantry.query.client import GantryQuery
from gantry.query.core.dataframe import GantrySeries
from gantry.query.globals import _query_alias, validate_init


@_query_alias
def accuracy_score(
    outputs: GantrySeries,
    feedback: GantrySeries,
    dropna: bool = False,
    num_points: int = 1,
) -> pd.DataFrame:
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.metric.accuracy_score(**locals())


@_query_alias
def mean_squared_error(
    outputs: GantrySeries,
    feedback: GantrySeries,
    dropna: bool = False,
    num_points: int = 1,
    multioutput: Literal["uniform_average", "raw_values"] = "uniform_average",
    squared: bool = True,
) -> pd.DataFrame:
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.metric.mean_squared_error(**locals())


@_query_alias
def confusion_matrix(
    outputs: GantrySeries,
    feedback: GantrySeries,
    dropna: bool = False,
    num_points: int = 1,
) -> pd.DataFrame:
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.metric.confusion_matrix(**locals())


@_query_alias
def f1_score(
    outputs: GantrySeries,
    feedback: GantrySeries,
    dropna: bool = False,
    num_points: int = 1,
    average: Literal["micro"] = "micro",
) -> pd.DataFrame:
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.metric.f1_score(**locals())


@_query_alias
def r2_score(
    outputs: GantrySeries,
    feedback: GantrySeries,
    dropna: bool = False,
    num_points: int = 1,
    multioutput: Literal["uniform_average", "raw_values", "variance_weighted"] = "uniform_average",
) -> float:
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.metric.r2_score(**locals())


@_query_alias
def precision_score(
    outputs: GantrySeries,
    feedback: GantrySeries,
    dropna: bool = False,
    num_points: int = 1,
    average: Literal["micro"] = "micro",
) -> pd.DataFrame:
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.metric.precision_score(**locals())


@_query_alias
def recall_score(
    outputs: GantrySeries,
    feedback: GantrySeries,
    dropna: bool = False,
    num_points: int = 1,
    average: Literal["micro"] = "micro",
) -> pd.DataFrame:
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.metric.recall_score(**locals())


@_query_alias
def roc_auc_score(
    outputs: GantrySeries,
    feedback: GantrySeries,
    dropna: bool = False,
    num_points: int = 1,
) -> pd.DataFrame:
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.metric.roc_auc_score(**locals())


@_query_alias
def percent_null(
    data_node: GantrySeries,
    dropna: bool = False,
    num_points: int = 1,
) -> pd.DataFrame:
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.metric.percent_null(**locals())


@_query_alias
def percent_true(
    data_node: GantrySeries,
    dropna: bool = False,
    num_points: int = 1,
) -> pd.DataFrame:
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.metric.percent_true(**locals())


@_query_alias
def percent_false(
    data_node: GantrySeries,
    dropna: bool = False,
    num_points: int = 1,
) -> pd.DataFrame:
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.metric.percent_false(**locals())
