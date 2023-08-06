from collections import OrderedDict

import mock
import pandas as pd
import pytest
import responses
from pandas.testing import assert_frame_equal
from responses import matchers

from gantry.query.core.dataframe import Filters, GantryDataFrame

from ..conftest import DATA, END_TIME, MULTIPLE_FEATURES_INT_DATA, ORIGIN, START_TIME


@pytest.fixture
@mock.patch("gantry.query.core.dataframe.GantryDataFrame._build_series")
def df(mock_populate, api_client_obj):
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
            filters=[],
        )


@pytest.fixture
@mock.patch(
    "gantry.query.core.queryframe.GantryQueryFrame.metadata",
    return_value=MULTIPLE_FEATURES_INT_DATA,
    new_callable=mock.PropertyMock,
)
@mock.patch("gantry.query.core.dataframe.get_application_node_id")
def df_with_int(get_application_node_id_mock, metadata, api_client_obj):
    get_application_node_id_mock.return_value = "12345"
    return GantryDataFrame(
        api_client=api_client_obj,
        application="foobar",
        version="1.2.3",
        env="dev",
        start_time=START_TIME,
        end_time=END_TIME,
        filters=[],
    )


def test_build_series(df):
    content = {
        "end_time": "2008-09-10 23:58:23",
        "start_time": "2008-09-03 20:56:35",
        "version": "1.2.3",
    }

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}/api/v1/models/foobar/schemas".format(ORIGIN),
            json={"response": "ok", "data": DATA},
            match=[matchers.query_param_matcher(content)],
        )

        series = df._build_series()
        assert len(series) == 3

        assert "pred_datanode" in series
        assert series["pred_datanode"].dtype == "intA"
        assert series["pred_datanode"].series_type == "A"

        assert "feed_datanode" in series
        assert series["feed_datanode"].dtype == "intB"
        assert series["feed_datanode"].series_type == "B"

        assert "proj_datanode" in series
        assert series["proj_datanode"].dtype == "intC"
        assert series["proj_datanode"].series_type == "C"


def test_clone_with_extra_filters_error(df, series_obj):
    f = Filters._from_single_filter({"foo": "bar"}, series_obj)
    with pytest.raises(ValueError):
        df._clone_with_extra_filters(f)


@mock.patch(
    "gantry.query.core.queryframe.GantryQueryFrame.metadata",
    return_value=MULTIPLE_FEATURES_INT_DATA,
    new_callable=mock.PropertyMock,
)
@mock.patch("gantry.query.core.dataframe.get_application_node_id")
def test_clone_with_extra_filters(
    get_application_node_id_mock, metadata, df_factory, series_obj, api_client_obj
):
    get_application_node_id_mock.return_value = "12345"
    df = GantryDataFrame(
        api_client=api_client_obj,
        application="foobar",
        version="1.2.3",
        env="dev",
        start_time=START_TIME,
        end_time=END_TIME,
        filters=[{"bar": "baz"}],
    )
    series_obj.parent_dataframe = df
    f = Filters._from_single_filter({"foo": "bar"}, series_obj)

    another_df = df._clone_with_extra_filters(f)

    assert another_df.filters == [{"bar": "baz"}, {"foo": "bar"}]


@mock.patch(
    "gantry.query.core.queryframe.GantryQueryFrame.metadata",
    return_value=DATA,
    new_callable=mock.PropertyMock,
)
def test_dtypes(meta, df):
    assert isinstance(df.dtypes, pd.Series)
    expected = pd.Series(
        {
            "feed_datanode": "intB",
            "pred_datanode": "intA",
            "proj_datanode": "intC",
        }
    )
    pd.testing.assert_series_equal(df.dtypes, expected)


def test_inexistent_attr(df):
    with pytest.raises(AttributeError, match="some_inexistent_attr is not a valid attribute"):
        _ = df.some_inexistent_attr


def test_inexistent_key(df):
    with pytest.raises(KeyError, match="some_inexistent_col is not a valid column"):
        _ = df["some_inexistent_col"]


@pytest.mark.parametrize("n", [1, 5, 10, 11])
@mock.patch("gantry.query.core.dataframe.GantryQueryFrame._populate_raw_request")
@mock.patch("gantry.query.core.dataframe.GantryQueryFrame._prepare_pandas_dataframe")
def test_head(mock_df, mock_data, n, df):
    total_num_events = 10
    all_events = list(range(total_num_events))
    mock_data.return_value = all_events[:n]
    mock_df.return_value = pd.DataFrame({"foo": mock_data.return_value})
    pd.testing.assert_frame_equal(df.head(n), mock_df.return_value)


@pytest.mark.parametrize("n", [1, 5, 10, 11])
@mock.patch("gantry.query.core.dataframe.GantryQueryFrame._populate_raw_request")
@mock.patch("gantry.query.core.dataframe.GantryQueryFrame._prepare_pandas_dataframe")
def test_tail(mock_df, mock_data, n, df):
    total_num_events = 10
    all_events = list(range(total_num_events))
    mock_data.return_value = all_events[:n]
    mock_df.return_value = pd.DataFrame({"foo": mock_data.return_value})
    pd.testing.assert_frame_equal(df.tail(n), mock_df.return_value)


@mock.patch("gantry.query.core.dataframe.GantryQueryFrame._populate_raw_request")
@mock.patch("gantry.query.core.dataframe.GantryQueryFrame._prepare_pandas_dataframe")
def test_fetch(mock_df, mock_data, df):
    total_num_events = 10
    all_events = list(range(total_num_events))
    mock_data.return_value = all_events
    mock_df.return_value = pd.DataFrame({"foo": mock_data.return_value})
    pd.testing.assert_frame_equal(df.fetch(), mock_df.return_value)


@mock.patch("gantry.query.core.dataframe.GantrySeries._describe")
@mock.patch("gantry.query.core.dataframe.GantryDataFrame._build_series")
def test_describe(mock_build_series, mock_series_describe, df, series_obj_1):
    df.series = OrderedDict({"s1": series_obj_1, "s2": series_obj_1})
    mock_series_describe.side_effect = [{"foo": "bar"}, {"foo": "baz"}]
    expected = pd.DataFrame(
        [
            ["foobar", "foobar"],
            [START_TIME, START_TIME],
            [END_TIME, END_TIME],
            ["bar", "baz"],
        ],
        index=["application", "from", "to", "foo"],
        columns=["s1", "s2"],
    )
    assert_frame_equal(df.describe(), expected)


# Test drive development here
def test_parent_filters(df_factory, series_obj_factory):
    # Create df with a series feature and existing filters
    existing_filters = [mock.Mock()]
    df = df_factory(existing_filters)
    series = series_obj_factory(datatype="int", parent_dataframe=df)
    df.series = {"series_name": series}

    # This action shouldn't change the df filters
    _ = df["series_name"] > 10
    assert len(df.filters) == 1


@mock.patch(
    "gantry.query.core.queryframe.GantryQueryFrame.metadata",
    return_value=MULTIPLE_FEATURES_INT_DATA,
    new_callable=mock.PropertyMock,
)
@mock.patch("gantry.query.core.dataframe.get_application_node_id")
def test_parent_filters_resolve(get_application_node_id_mock, metadata, api_client_obj):
    get_application_node_id_mock.return_value = "12345"
    df = GantryDataFrame(
        api_client=api_client_obj,
        application="foobar",
        version="1.2.3",
        env="dev",
        start_time=START_TIME,
        end_time=END_TIME,
        filters=[],
    )

    _ = df[df["A"] > 10]
    other_df_with_filters = df[df["A"] < 20]

    # This series should have only 1 filter, the < 20 restriction
    # If this doesn't happen, it means that all mehtods using
    # _aggregate_query will not work.
    assert len(other_df_with_filters["A"].parent_dataframe.filters) == 1


def test_filtering_using_other_df(df, df_with_int):
    with pytest.raises(ValueError):
        _ = df[df_with_int["A"] > 10]


VIEWS_DATA = [
    {
        "name": "foobar",
        "start_time": START_TIME.isoformat(),
        "end_time": END_TIME.isoformat(),
        "tag_filters": {"env": "barbaz"},
        "data_filters": [{"XYZ": "123"}],
    },
]


@mock.patch(
    "gantry.query.core.queryframe.GantryQueryFrame.metadata",
    return_value=MULTIPLE_FEATURES_INT_DATA,
    new_callable=mock.PropertyMock,
)
@mock.patch("gantry.query.core.dataframe.get_application_node_id")
@mock.patch("gantry.query.core.dataframe.get_start_end_time_from_view")
def test_from_view_factory(mock_get_times, get_application_node_id_mock, metadata, api_client_obj):
    mock_get_times.return_value = (START_TIME, END_TIME)
    get_application_node_id_mock.return_value = "12345"
    version = "0.1.2"

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}/api/v1/applications/app/views?version={}".format(ORIGIN, version),
            json={"response": "ok", "data": VIEWS_DATA},
        )

        rsps.add(
            responses.GET,
            "{}/api/v1/models/app/schemas".format(ORIGIN),
            json={"response": "ok", "data": {"version": version}},
        )

        df = GantryDataFrame.from_view(
            api_client=api_client_obj,
            application="app",
            view="foobar",
            version=None,
            environment="barbaz",
        )

    assert df.filters == [{"XYZ": "123"}]
    assert df.query_info.start_time == START_TIME
    assert df.query_info.end_time == END_TIME
    assert df.query_info.version == "0.1.2"
    assert df.query_info.environment == "barbaz"
    assert df.query_info.application == "app"
    assert df.query_info.application_node_id == "12345"
    assert df.api_client is api_client_obj
    assert df.series.keys() == set(["A", "B"])

    mock_get_times.assert_called_with(VIEWS_DATA[0])


@pytest.mark.parametrize(
    ["view", "environment"],
    [
        ("invalid", "barbaz"),
        ("foobar", "invalid"),
    ],
)
@mock.patch("gantry.query.core.dataframe.get_application_node_id")
def test_from_view_factory_error(
    get_last_application_version_mock, view, environment, api_client_obj
):
    version = "0.1.2"
    get_last_application_version_mock.return_value = version
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}/api/v1/applications/app/views?version={}".format(ORIGIN, version),
            json={"response": "ok", "data": VIEWS_DATA},
        )

        with pytest.raises(RuntimeError):
            _ = GantryDataFrame.from_view(
                api_client=api_client_obj,
                application="app",
                view=view,
                version=version,
                environment=environment,
            )
