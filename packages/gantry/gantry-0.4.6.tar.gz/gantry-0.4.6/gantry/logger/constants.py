from enum import Enum


class BatchTypes(Enum):
    RECORD = "RECORD"
    FEEDBACK = "FEEDBACK"
    PREDICTION = "PREDICTION"
    FILE = "FILE"


class UploadFileType(str, Enum):
    CSV_WITH_HEADERS = "CSV_WITH_HEADERS"


class Delimiter(Enum):
    COMMA = ","


CHUNK_SIZE = 10 * 1024 * 1024  # File upload chunk size 10 MB
