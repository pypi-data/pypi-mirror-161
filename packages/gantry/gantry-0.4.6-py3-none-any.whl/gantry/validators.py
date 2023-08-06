from typing import List, Optional

from gantry.exceptions import GantryLoggingDataTypeError

MAX_CALL_DEPTH = 10


SUPPORTED_DRUID_TYPES = (int, str, float, bool, type(None))


def validate_logged_field_datatype(field, paths: Optional[List[str]] = None) -> None:
    """
    Validates that fields is:
        a valid primitive type
        OR
        a list that is no larger than 2 dimensions and contains valid primitive types
        OR
        a dict that is no larger than 10 levels and contains valid primitive types
    """
    paths = paths or []

    if isinstance(field, list) or isinstance(field, tuple):
        for i, item in enumerate(field):
            # a list item can be a primitive type
            if _validate_primitive_type(item):
                continue

            # or it can be a 1-dimensional list containing primitive types
            if isinstance(item, list):
                for j, nested_item in enumerate(item):
                    if not _validate_primitive_type(nested_item):
                        full_path = ".".join(paths) + f"[{i}][{j}]"
                        field_type = type(field)
                        raise GantryLoggingDataTypeError(
                            (
                                "{} is not a valid Gantry datatype. "
                                "Lists must be 1- or 2-dimensional and contain only primitive "
                                "types."
                            ).format(
                                full_path,
                            )
                        )
            else:
                full_path = ".".join(paths) + f"[{i}]"
                item_type = type(item)
                raise GantryLoggingDataTypeError(
                    (
                        "{} with type {} is not a valid Gantry datatype. "
                        "Lists must be 1- or 2-dimensional and contain only primitive types."
                    ).format(
                        full_path,
                        item_type,
                    )
                )
    elif isinstance(field, dict):
        for k, v in field.items():
            validate_logged_field_datatype(k, paths=(paths + [str(k), "key"]))
            validate_logged_field_datatype(v, paths=(paths + [str(k), "value"]))
    else:
        if _validate_primitive_type(field):
            return

        full_path = ".".join(paths)
        field_type = type(field)
        raise GantryLoggingDataTypeError(
            "{} with type {} is not a valid Gantry datatype".format(full_path, field_type)
        )


def _validate_primitive_type(field) -> bool:
    return any(isinstance(field, t) for t in SUPPORTED_DRUID_TYPES)
