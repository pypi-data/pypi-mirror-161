import pytest
import datetime
import pandas.api.types as ptypes
from gantry.data_generator.data_generator import generate_demo_data, _generate_batch_data


@pytest.mark.parametrize(
    "sample_size,expected_length",
    [
        (203, 203),
        (500, 500),
        (1000, 1000),
        (-2000, 200),
        (-200, 200),
        (-1, 200),
        (0, 200),
        (50, 200),
        (5000, 4000),
    ],
)
def test_generate_demo_data(sample_size, expected_length):
    data = generate_demo_data(sample_size)
    assert len(data) == expected_length
    assert ptypes.is_numeric_dtype(data["income"])
    assert ptypes.is_string_dtype(data["description"])
    assert all(ptypes.is_bool_dtype(data[col]) for col in ["prediction", "loan_repaid"])
    assert ptypes.is_categorical_dtype(data["credit_history"])
    assert ptypes.is_datetime64_any_dtype(data["timestamp"])
    assert max(data["timestamp"]) <= datetime.datetime.now()
    assert min(data["income"]) >= 5000


@pytest.mark.parametrize(
    "cred_hist_prop,pred_true_rate,loan_repaid_rate",
    [
        (-0.5, 0.2, 0.2),
        (0.2, -0.5, 0.2),
        (0.2, 0.2, -0.5),
        (0.2, 0.2, 2),
        (0.2, 2, 0.2),
        (2, 0.2, 0.2),
    ],
)
def test_generate_batch_data(cred_hist_prop, pred_true_rate, loan_repaid_rate):
    with pytest.raises(ValueError):
        _generate_batch_data(
            cred_hist_prop=cred_hist_prop,
            pred_true_rate=pred_true_rate,
            loan_repaid_rate=loan_repaid_rate,
        )
