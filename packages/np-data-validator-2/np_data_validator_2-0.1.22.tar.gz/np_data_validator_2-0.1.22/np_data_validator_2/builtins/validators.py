from typing import Any, List, Tuple

import operator
import os


def meets_filesize_threshold(
    value,
    threshold,
    operator_name: str = "ge",
) -> tuple[int, bool]:
    op = getattr(operator, operator_name)
    filesize = os.path.getsize(value)
    return (
        filesize,
        op(filesize, threshold),
    )


def has_dict_key(value, path: list[str]) -> tuple[Any, bool]:
    try:
        for key in path:
            value = value[key]
        return (
            value,
            True,
        )
    except KeyError:
        return (
            None,
            False,
        )
