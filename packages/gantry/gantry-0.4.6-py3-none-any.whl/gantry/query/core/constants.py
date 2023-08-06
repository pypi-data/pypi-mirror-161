STATUS_PARAM = "response"
OK_STATUS = "ok"
ERR_STATUS = "error"

GENERIC_MESSAGE = "Request failed"

TIMEZONE = {"TO_TIMEZONE": "UTC"}

SCHEMA_TYPES = [
    "prediction_datanodes",
    "feedback_datanodes",
    "projection_datanodes",
]

MAX_SIZE_CACHE_B = 10 * (2**20)  # 10 MB
MAX_TTL_CACHE_SECS = 600  # 10 minutes
