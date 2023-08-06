import datetime

import mock
import pytest
import responses

from gantry.api_client import APIClient
from gantry.query.client import GantryQuery
from gantry.query.core import dataframe, queryframe
from gantry.query.core.dataframe import GantryDataFrame, GantrySeries

ORIGIN = "https://gantry-api:12345"
START_TIME = datetime.datetime(2008, 9, 3, 20, 56, 35)
END_TIME = datetime.datetime(2008, 9, 10, 23, 58, 23)

START_TIME_STR = START_TIME.isoformat()
END_TIME_STR = END_TIME.isoformat()

DATA = {
    "id": "ABCD1234",
    "prediction_datanodes": [
        {
            "name": "pred_datanode",
            "dtype": "intA",
            "event_type": "A",
            "node_metadata": {
                "content_retrieval": ["inputs", "pred_datanode"],
                "dtype": {"id_str": False, "is_categorical": False, "long_str": False},
            },
            "id": "ABCD1234",
        },
    ],
    "feedback_datanodes": [
        {
            "name": "feed_datanode",
            "dtype": "intB",
            "event_type": "B",
            "node_metadata": {
                "content_retrieval": ["inputs", "feed_datanode"],
                "dtype": {"id_str": False, "is_categorical": False, "long_str": False},
            },
            "id": "ABCD1234",
        },
    ],
    "projection_datanodes": [
        {
            "name": "proj_datanode",
            "dtype": "intC",
            "event_type": "C",
            "node_metadata": {
                "content_retrieval": ["inputs", "proj_datanode"],
                "dtype": {"id_str": False, "is_categorical": False, "long_str": False},
            },
            "id": "ABCD1234",
        },
    ],
}


MULTIPLE_FEATURES_INT_DATA = {
    "id": "ABCD1234",
    "prediction_datanodes": [
        {
            "name": "A",
            "dtype": "int",
            "event_type": "prediction",
            "node_metadata": {
                "content_retrieval": ["inputs", "pred_datanode"],
                "dtype": {"id_str": False, "is_categorical": False, "long_str": False},
            },
            "id": "ABCD1234",
        },
        {
            "name": "B",
            "dtype": "int",
            "event_type": "prediction",
            "node_metadata": {
                "content_retrieval": ["inputs", "pred_datanode"],
                "dtype": {"id_str": False, "is_categorical": False, "long_str": False},
            },
            "id": "ABCD1234",
        },
    ],
    "feedback_datanodes": [],
    "projection_datanodes": [],
}


def to_tz_time(dt_timestamp):
    return dt_timestamp.isoformat() + "Z"


@pytest.fixture
def query_info_obj():
    application_node_id = "af0d0317-adbf-4524-b838-9dddf1c43fc8"
    application = "foobar"
    version = "1.2.3"
    environment = "dev"

    return queryframe.QueryInfo(
        application_node_id, application, version, environment, START_TIME, END_TIME
    )


@pytest.fixture
def api_client_obj():
    return APIClient(origin=ORIGIN, api_key="abcd1234")


@pytest.fixture
def gantry_query_obj(api_client_obj):
    return GantryQuery(api_client_obj)


@pytest.fixture
@mock.patch("gantry.query.core.dataframe.GantryDataFrame._build_series")
def df_factory(mock_populate, api_client_obj):
    def wrapper(filters):
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "{}/api/v1/models/foobar/schemas".format(ORIGIN),
                json={"response": "ok", "data": DATA},
            )

            return GantryDataFrame(
                api_client=api_client_obj,
                application="foobar",
                version="1.2.3",
                env="dev",
                start_time=START_TIME,
                end_time=END_TIME,
                filters=filters,
            )

    return wrapper


@pytest.fixture
def series_obj_1(api_client_obj, query_info_obj):
    series = GantrySeries(
        name="foo",
        datatype="int",
        series_type="prediction",
        parent_dataframe=mock.Mock(api_client=api_client_obj, query_info=query_info_obj),
        id="abc",
    )
    series.count = mock.Mock(return_value=10)
    return series


@pytest.fixture
def series_obj_2(api_client_obj, query_info_obj):
    series = GantrySeries(
        name="bar",
        datatype="int",
        series_type="prediction",
        parent_dataframe=mock.Mock(api_client=api_client_obj, query_info=query_info_obj),
        id="abc",
    )
    series.count = mock.Mock(return_value=10)
    return series


@pytest.fixture
def series_obj(api_client_obj, query_info_obj):
    return dataframe.GantrySeries(
        name="series_name",
        datatype="int",
        series_type="prediction",
        parent_dataframe=mock.Mock(api_client=api_client_obj, query_info=query_info_obj),
        id="abc123",
    )


@pytest.fixture
def series_obj_factory(api_client_obj, query_info_obj):
    def wrapper(datatype, parent_dataframe=None, name="series_name", count=10):
        series = dataframe.GantrySeries(
            name=name,
            datatype=datatype,
            series_type="prediction",
            parent_dataframe=parent_dataframe
            if parent_dataframe is not None
            else mock.Mock(api_client=api_client_obj, query_info=query_info_obj),
            id="abc123",
        )
        series.count = mock.Mock(return_value=count)
        return series

    return wrapper


@pytest.fixture
def series_obj_factory_with_filters(df_factory, api_client_obj, query_info_obj):
    def wrapper(datatype, filters):
        return dataframe.GantrySeries(
            name="series_name",
            datatype=datatype,
            series_type="prediction",
            parent_dataframe=df_factory(filters=filters),
            id="abc123",
        )

    return wrapper
