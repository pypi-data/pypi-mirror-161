from gantry.query import globals
from gantry.query.client import GantryQuery
from gantry.query.core.dataframe import GantrySeries
from gantry.query.globals import _query_alias, validate_init


@_query_alias
def d1(feat1: GantrySeries, feat2: GantrySeries) -> float:
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.distance.d1(**locals())


@_query_alias
def dinf(feat1: GantrySeries, feat2: GantrySeries) -> float:
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.distance.dinf(**locals())


@_query_alias
def ks(feat1: GantrySeries, feat2: GantrySeries) -> float:
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.distance.ks(**locals())


@_query_alias
def kl(feat1: GantrySeries, feat2: GantrySeries) -> float:
    validate_init()
    assert isinstance(globals._Query, GantryQuery)  # mypy bug- mypy/issues/4805
    return globals._Query.distance.kl(**locals())
