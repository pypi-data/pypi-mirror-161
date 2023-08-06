import mock
import pytest
import responses
from responses import matchers

from gantry.api_client import APIClient
from gantry.query.client import GantryQuery
from gantry.query.core.dataframe import GantryDataFrame

from .conftest import END_TIME, ORIGIN, START_TIME


@pytest.fixture
def gantry_query_obj():
    api_client = APIClient(origin=ORIGIN, api_key="abcd1234")
    return GantryQuery(api_client)


@pytest.mark.parametrize(
    ["data", "expected"],
    [
        ({"application_1": {}, "application_2": {}}, ["application_1", "application_2"]),
        (
            {
                "application": {},
            },
            ["application"],
        ),
        ({}, []),
    ],
)
def test_list_applications(data, expected, gantry_query_obj):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}/api/v1/models".format(ORIGIN),
            match=[matchers.query_param_matcher({"limit": "10"})],
            json={
                "response": "ok",
                "data": data,
            },
        )

        assert gantry_query_obj.list_applications() == expected


@pytest.mark.parametrize(
    ["versions", "expected"],
    [
        ([{"internal_version": 10, "version": "baz"}], [(10, "baz")]),
        (
            [
                {"internal_version": 10, "version": "baz"},
                {"internal_version": 20, "version": "bar"},
            ],
            [(10, "baz"), (20, "bar")],
        ),
        ([], []),
    ],
)
def test_list_application_versions(versions, expected, gantry_query_obj):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}/api/v1/models/foobar".format(ORIGIN),
            match=[matchers.query_param_matcher({"include_names": "True"})],
            json={"response": "ok", "data": {"versions": versions}},
        )

        assert gantry_query_obj.list_application_versions("foobar") == expected


@pytest.mark.parametrize(
    ["envs", "expected"],
    [
        (["A", "B", "C"], ["A", "B", "C"]),
        ([], []),
    ],
)
def test_list_application_environments(envs, expected, gantry_query_obj):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}/api/v1/models/foobar".format(ORIGIN),
            json={"response": "ok", "data": {"environments": envs}},
        )

        assert gantry_query_obj.list_application_environments("foobar") == expected


def test_query(gantry_query_obj):
    application = "foobar"
    version = "1.2.3"
    environment = "env"

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}/api/v1/models/foobar/schemas".format(ORIGIN),
            json={"response": "ok", "data": {"id": "ABCD1234", "environments": []}},
            match=[
                matchers.query_param_matcher(
                    {
                        "end_time": "2008-09-10 23:58:23",
                        "start_time": "2008-09-03 20:56:35",
                        "version": "1.2.3",
                    }
                )
            ],
        )

        gantry_df = gantry_query_obj.query(
            application, START_TIME, END_TIME, version, environment, [{"filter": "foobar"}]
        )

        assert isinstance(gantry_df, GantryDataFrame)
        assert gantry_df.api_client == gantry_query_obj._api_client
        assert gantry_df.filters == [{"filter": "foobar"}]

        assert gantry_df.query_info.application == application
        assert gantry_df.query_info.version == version
        assert gantry_df.query_info.environment == environment
        assert gantry_df.query_info.start_time == START_TIME
        assert gantry_df.query_info.end_time == END_TIME


@mock.patch("gantry.query.client.GantryDataFrame.from_view")
@mock.patch("gantry.query.client.GantryQuery.list_application_views")
def test_query_with_view(mock_application_views, mock_factory, gantry_query_obj):
    mock_application_views.return_value = ["barbaz"]
    mock_factory.return_value = "data"

    assert (
        gantry_query_obj.query("foobar", version="1.2.3", environment="foo", view="barbaz")
        == "data"
    )
    mock_factory.assert_called_once_with(
        gantry_query_obj._api_client, "foobar", "barbaz", "1.2.3", "foo"
    )


@mock.patch("gantry.query.client.GantryQuery.list_application_views")
def test_query_with_view_not_found(mock_application_views, gantry_query_obj):
    mock_application_views.return_value = ["A", "B", "C"]

    with pytest.raises(ValueError):
        _ = gantry_query_obj.query("foobar", view="not-found")


@pytest.mark.parametrize(
    ["start_time", "end_time", "filters"],
    [
        (START_TIME, None, None),
        (START_TIME, None, {}),
        (START_TIME, END_TIME, None),
        (None, END_TIME, {}),
        (None, END_TIME, None),
        (START_TIME, END_TIME, {"foo": "bar"}),
        (None, None, {"foo": "bar"}),
        (None, END_TIME, {"foo": "bar"}),
        (START_TIME, None, {"foo": "bar"}),
        (None, None, {}),
    ],
)
def test_query_invalid_call_with_view_and_others(start_time, end_time, filters, gantry_query_obj):
    with pytest.raises(ValueError):
        _ = gantry_query_obj.query("foobar", start_time, end_time, filters=filters, view="foobar")


def test_set_reference(gantry_query_obj):
    application = "foobar"
    version = "1.2.3"
    reference_name = "barbaz"
    tags = {"a": "b"}

    content = {
        "name": reference_name,
        "version": version,
        "start_time": "2008-09-03T20:56:35Z",
        "end_time": "2008-09-10T23:58:23Z",
        "tags": tags,
    }

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "{}/api/v1/models/foobar/references".format(ORIGIN),
            json={"response": "ok", "reference_id": "ABCD1234"},
            match=[matchers.json_params_matcher(content)],
        )

        assert (
            gantry_query_obj.set_reference(
                application, version, START_TIME, END_TIME, reference_name, tags
            )
            == "ABCD1234"
        )


def test_get_current_feedback_schema(gantry_query_obj):
    with pytest.raises(NotImplementedError):
        gantry_query_obj.get_current_metric_schema("application")


def test_update_feedback_schema(gantry_query_obj):
    with pytest.raises(NotImplementedError):
        gantry_query_obj.update_feedback_schema("application", [])


def test_add_feedback_field(gantry_query_obj):
    with pytest.raises(NotImplementedError):
        gantry_query_obj.add_feedback_field("application", {})


def test_get_current_metric_schema(gantry_query_obj):
    with pytest.raises(NotImplementedError):
        gantry_query_obj.get_current_metric_schema("application")


def test_update_metric_schema(gantry_query_obj):
    with pytest.raises(NotImplementedError):
        gantry_query_obj.update_metric_schema("application", [])


def test_add_metric(gantry_query_obj):
    with pytest.raises(NotImplementedError):
        gantry_query_obj.add_metric("application", {})


VIEWS_DATA = [
    {"name": "view_1", "tag_filters": {"env": "env-A"}, "other": "A"},
    {"name": "view_2", "tag_filters": {"env": "env-B"}, "other": "B"},
    {"name": "view_3", "tag_filters": {"env": "env-B"}, "other": "C"},
]


@pytest.mark.parametrize(
    ["env", "response_data", "expected", "version"],
    [("dev", [], [], "1.2.3"), ("env-A", VIEWS_DATA, ["view_1"], "1.2.3")],
)
def test_list_application_views_with_other_env(
    gantry_query_obj, env, response_data, expected, version
):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}/api/v1/applications/barbaz/views?version={}".format(ORIGIN, version),
            json={
                "response": "ok",
                "data": response_data,
            },
        )

        assert (
            gantry_query_obj.list_application_views("barbaz", version="1.2.3", environment=env)
            == expected
        )


@pytest.mark.parametrize(
    ["response_data", "version"],
    [([], "1.2.3"), (VIEWS_DATA, "1.2.3")],
)
def test_print_application_info(response_data, version, gantry_query_obj):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}/api/v1/models/barbaz".format(ORIGIN),
            json={
                "response": "ok",
                "data": {
                    "versions": [
                        {"internal_version": 10, "version": version},
                    ],
                    "environments": ["dev", "prod"],
                },
            },
        )
        rsps.add(
            responses.GET,
            "{}/api/v1/applications/barbaz/views".format(ORIGIN),
            json={
                "response": "ok",
                "data": response_data,
            },
            match=[matchers.query_param_matcher({"version": version})],
        )

        assert gantry_query_obj.print_application_info("barbaz") is None
