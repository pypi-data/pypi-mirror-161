import mock
import pytest

from gantry.query.client import GantryQuery
from gantry.query.distance import main


@pytest.mark.parametrize(
    "method",
    [
        "d1",
        "dinf",
        "ks",
        "kl",
    ],
)
@mock.patch("gantry.query.main.globals._Query", spec=GantryQuery)
def test_proxy_methods(mock_query, method, series_obj_1, series_obj_2):
    mock_query.distance = mock.Mock()
    getattr(mock_query.distance, method).return_value = "foo"
    assert getattr(main, method)(series_obj_1, series_obj_2) == "foo"
    getattr(mock_query.distance, method).assert_called_once_with(
        feat1=series_obj_1, feat2=series_obj_2
    )
