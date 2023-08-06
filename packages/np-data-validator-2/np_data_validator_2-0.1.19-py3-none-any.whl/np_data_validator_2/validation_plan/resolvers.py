from typing import Any, Optional, Tuple

import glob
import logging
import os

from ..dataclasses import ProcessorResult, Validator

logger = logging.getLogger(__name__)


def resolve_local_filepath(glob_pattern: str, local_dir: str) -> str:
    resolved = glob.glob(os.path.join(local_dir, glob_pattern))
    if len(resolved) > 1:
        # logger.info("Multiple files globbed: %s" % resolved)  # todo add logging
        raise Exception("Multiple files globbed: %s" % resolved)
    if len(resolved) != 1:
        raise Exception(
            "No files globbed for glob_pattern=%s local_dir=%s", glob_pattern, local_dir
        )
    return resolved[0]
