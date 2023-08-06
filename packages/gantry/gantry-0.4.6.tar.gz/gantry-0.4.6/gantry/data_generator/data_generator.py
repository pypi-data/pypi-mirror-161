from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import uuid
import random
import logging

logger = logging.getLogger(__name__)

RANDOM_SEED = 43
DEFAULT_SAMPLE_SIZE = 2000
MIN_SAMPLE_SIZE = 200
MAX_SAMPLE_SIZE = 4000

# Generate random description
PRONOUNS = ["He", "She"]
VERBS = ["was", "is", "used to be", "wants to become"]
NOUNS = [
    "a doctor.",
    "an engineer.",
    "a infuluencer.",
    "a dancer.",
    "a lyft driver.",
    "a pilot" "a singer.",
    "a freelancer.",
    "a teacher.",
    "a professor.",
]


def _generate_batch_data(
    batch_size: int = 1000,
    cred_hist_prop: float = 0.7,
    pred_true_rate: float = 0.6,
    loan_repaid_rate: float = 0.8,
    random_seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """
    Generate a single batch data. You can control the data
    distribution by changing the input parameters

    Args:
        batch_size(int, defaults to 1000): size of the data
        cred_hist_prop(float, defaults to 0.7): Ratio of customers who have good credit history
        pred_true_rate(float, defaults to 0.6): Positive prediction ratio
        loan_repaid_rate(float, defaults to 0.8): Positive feedback ratio
        ramdom_seed(int, default to 43): random seed
    Returns:
        pd.DataFrame which contain the generated data
    """
    if any(param < 0 or param > 1 for param in [cred_hist_prop, pred_true_rate, loan_repaid_rate]):
        raise ValueError("Must be a value between 0 and 1")

    rng = np.random.default_rng(random_seed)
    credit_history_categorical = rng.choice(
        ["Good", "Bad"], batch_size, p=[cred_hist_prop, 1 - cred_hist_prop]
    )

    income = rng.normal(loc=50000, scale=15000, size=batch_size)
    income = np.clip(income, 10000, 200000).astype(int)

    predictions = rng.uniform(size=batch_size) < pred_true_rate
    loan_repaid = rng.uniform(size=batch_size) < loan_repaid_rate

    rand_pronouns = rng.choice(PRONOUNS, batch_size)
    rand_verbs = rng.choice(VERBS, batch_size)
    rand_nouns = rng.choice(NOUNS, batch_size)
    text = [" ".join([p, v, n]) for p, v, n in zip(rand_pronouns, rand_verbs, rand_nouns)]

    random.seed(random_seed)
    loan_ids = [str(uuid.UUID(int=random.getrandbits(128))) for _ in range(batch_size)]

    df = pd.DataFrame(
        {
            "loan_id": loan_ids,
            "credit_history": credit_history_categorical,
            "income": income,
            "description": text,
            "loan_repaid": loan_repaid,
            "prediction": predictions,
        }
    )
    df.credit_history = df.credit_history.astype("category")
    return df


def generate_demo_data(
    sample_size: int = DEFAULT_SAMPLE_SIZE, random_seed: int = RANDOM_SEED
) -> pd.DataFrame:
    """
    Function to generate synthetic data to be used for exploring Gantry features.
    This function will generate data points for the last 48 hours. The first 24
    hours' data has a different distribution with the second 24 hours' data.
    You can create views and compare the data drift/different.

    Note: data is randomly generated and should only be used for demo purposes.

    Args:
        sample_size (int, defaults to 2000): sample dataset size, sample size should
        be larger than 200 and smaller than 4000
        random_seed (int, default to 43): random seed
    Returns:
        pd.DataFrame which contain the generated data
    """
    if sample_size < MIN_SAMPLE_SIZE:
        sample_size = MIN_SAMPLE_SIZE
        logger.warn(
            f"sample_size smaller than {MIN_SAMPLE_SIZE}, will use {MIN_SAMPLE_SIZE} instead."
        )

    if sample_size > MAX_SAMPLE_SIZE:
        sample_size = MAX_SAMPLE_SIZE
        logger.warn(
            f"sample_size larger than {MAX_SAMPLE_SIZE}, will use {MAX_SAMPLE_SIZE} instead."
        )

    batch1_size = sample_size // 2 + sample_size % 2
    batch2_size = sample_size // 2

    batch_1 = _generate_batch_data(
        batch_size=batch1_size,
        cred_hist_prop=0.9,
        pred_true_rate=0.8,
        loan_repaid_rate=0.8,
        random_seed=random_seed,
    )

    batch_2 = _generate_batch_data(
        batch_size=batch2_size,
        cred_hist_prop=0.2,
        pred_true_rate=0.5,
        loan_repaid_rate=0.4,
        random_seed=random_seed,
    )

    end_time = datetime.now()
    mid_time = end_time - timedelta(seconds=86400)
    start_time = end_time - timedelta(seconds=172800)

    random.seed(random_seed)
    batch_1["timestamp"] = [
        start_time + timedelta(seconds=random.randint(0, 86399)) for _ in range(batch1_size)
    ]
    batch_2["timestamp"] = [
        mid_time + timedelta(seconds=random.randint(0, 86399)) for _ in range(batch2_size)
    ]

    return pd.concat([batch_1, batch_2])
