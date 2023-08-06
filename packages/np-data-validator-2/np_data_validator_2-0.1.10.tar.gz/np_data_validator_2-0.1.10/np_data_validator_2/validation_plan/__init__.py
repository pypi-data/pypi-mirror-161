from typing import Any, Callable, List, Optional, Tuple

import glob
import logging
import os
from dataclasses import replace

from .. import version
from ..checksum import generate_checksum
from ..dataclasses import (
    AssetValidationManifest,
    AssetValidationResult,
    Processor,
    ProcessorResult,
    ValidationManifest,
    ValidationResult,
    Validator,
)
from .resolvers import resolve_local_filepath

logger = logging.getLogger(__name__)


def resolve_args(
    validator: Validator,
    filepath: str,
    memo: dict,
) -> tuple[tuple[Any, dict], Optional[ProcessorResult]]:
    if not validator.processor:
        return (
            (
                filepath,
                validator.args,
            ),
            None,
        )

    processed = run_processor(validator.processor, filepath, memo)

    return (
        (
            processed.value,
            validator.args,
        ),
        processed,
    )


def run_processor(processor: Processor, filepath: str, memo: dict) -> ProcessorResult:
    if processor.name in memo:
        return ProcessorResult(
            value=memo[processor.name],
            from_memo=True,
        )

    value = processor.resolved_function(
        filepath,
        **processor.args,
    )

    # add to memo
    memo[processor.name] = value

    return ProcessorResult(
        value=value,
    )


def run_validator(
    validator: Validator,
    filepath: str,
    memo: dict,
) -> ValidationResult:
    args, processed = resolve_args(validator, filepath, memo)
    if processed:
        result = ValidationResult(
            name=validator.name,
            args=args,
            value=validator.resolved_function(args[0], **args[1]),
            processed=processed,
        )

        if not validator.processor.store_result:
            result = replace(
                result,
                processed=None,
                args=(
                    None,
                    args[1],
                ),
            )

        return result
    else:
        return ValidationResult(
            name=validator.name,
            args=args,
            value=validator.resolved_function(args[0], **args[1]),
        )


def run_asset_validation(
    lims_id: str,
    experiment_dir: str,
    filepath: str,
    manifest: AssetValidationManifest,
) -> AssetValidationResult:
    memo = {}
    validation = [
        run_validator(validator, filepath, memo) for validator in manifest.validators
    ]

    if not all(map(lambda result: result.value[1], validation)):
        logger.error("Failed validation: %s" % validation)

    return AssetValidationResult(
        version=version,
        lims_id=lims_id,
        filepath=filepath,
        experiment_dir=experiment_dir,
        validation=validation,
        checksum=generate_checksum(filepath),
        lims_verified=False,
        manifest=manifest,
    )


def run_experiment_validation(
    lims_id: str,
    experiment_dir: str,
    manifest: ValidationManifest,
) -> list[AssetValidationResult]:
    results = []
    for asset in manifest.assets:
        try:
            filepath = resolve_local_filepath(
                asset.glob_pattern,
                experiment_dir,
            )
            result = run_asset_validation(lims_id, experiment_dir, filepath, asset)
            results.append(result)
        except Exception as e:
            logger.error("Failed to validate asset: %s", asset, exc_info=True)

    return results
