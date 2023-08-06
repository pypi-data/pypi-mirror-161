import inspect
from typing import Optional

from gantry.exceptions import GantryException
from gantry.query.client import GantryQuery
from gantry.query.core.distance import GantryDistance
from gantry.query.core.metric import GantryMetric

_Query: Optional[GantryQuery] = None


def _query_alias(f):
    doc: str = ""
    orig_doc: Optional[str] = None
    if hasattr(GantryQuery, f.__name__):
        doc = "Alias for :meth:`gantry.query.core.GantryQuery.{}`".format(f.__name__)
        orig_doc = inspect.getdoc(getattr(GantryQuery, f.__name__))
    elif hasattr(GantryDistance, f.__name__):
        doc = "Alias for :meth:`gantry.query.core.GantryDistance.{}`".format(f.__name__)
        orig_doc = inspect.getdoc(getattr(GantryDistance, f.__name__))
    elif hasattr(GantryMetric, f.__name__):
        doc = "Alias for :meth:`gantry.query.core.GantryMetric.{}`".format(f.__name__)
        orig_doc = inspect.getdoc(getattr(GantryMetric, f.__name__))

    if orig_doc:
        doc += "\n\n{}".format(orig_doc)

    f.__doc__ = doc
    return f


def validate_init():
    if _Query is None:
        raise GantryException("Query functionality has not been initialized with a backend.")
