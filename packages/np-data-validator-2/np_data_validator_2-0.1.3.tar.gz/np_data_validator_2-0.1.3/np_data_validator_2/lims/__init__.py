from typing import List, Union

import logging
from dataclasses import replace

from ..checksum import generate_checksum
from ..dataclasses import AssetValidationResult
from .queries import EXP_QUERY, IMAGE_QUERY, PROBE_QUERY

logger = logging.getLogger(__name__)


def _validate(
    asset: AssetValidationResult, lims_path: str
) -> Union[AssetValidationResult, None]:
    lims_checksum = generate_checksum(lims_path)
    if asset.checksum == lims_checksum:
        return replace(asset, lims_verified=True)
    else:
        logger.error(
            "Checksum mismatch: current=%s, lims=%s"
            % (
                asset.checksum,
                lims_checksum,
            )
        )


def _validate_assets(
    cursor,
    query_template: str,
    lims_id: str,
    name_key: str,
    path_key: str,
    assets: list[AssetValidationResult],
) -> list[AssetValidationResult]:
    cursor.execute(query_template.format(lims_id))
    validated = []
    for row in cursor.fetchall():
        name = row[name_key]
        path = row[path_key]
        for asset in filter(lambda asset: asset.manifest.asset_type == name, assets):
            result = _validate(asset, path)
            if result is not None:
                validated.append(result)

    return validated


def validate_lims(
    cursor, lims_id: str, assets: list[AssetValidationResult]
) -> list[AssetValidationResult]:
    return [
        *_validate_assets(cursor, EXP_QUERY, lims_id, "wkft", "wkf_path", assets),
        *_validate_assets(
            cursor, IMAGE_QUERY, lims_id, "image_type", "image_path", assets
        ),
        *_validate_assets(cursor, PROBE_QUERY, lims_id, "ep", "wkf_path", assets),
    ]
