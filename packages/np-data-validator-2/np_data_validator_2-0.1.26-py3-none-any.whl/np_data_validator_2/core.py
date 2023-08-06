import json
import logging
import os

from .lims import validate_lims
from .storage import (
    get_asset_validation_results,
    get_validation_manifest,
    put_asset_validation_result,
    put_validation_manifest,
    update_asset_validation_result,
)
from .transformers import to_AssetValidationResult, to_ValidationManifest
from .validation_plan import run_experiment_validation

logger = logging.getLogger(__name__)


# this is designed to be called in python so has no file reading etc
def create_validation_manifest_from_json(
    client,
    manifest_path: str,
    table_name: str = "dev",
):
    with open(manifest_path) as f:
        data = json.load(f)

    manifest = to_ValidationManifest(data)

    return put_validation_manifest(
        client[table_name].manifest,
        manifest,
    )


def validate_local_experiment(
    client,
    lims_id: str,
    manifest_name: str,
    experiment_dir: str,
    table_name: str = "dev",
):
    manifest = get_validation_manifest(
        client[table_name].manifest,
        manifest_name,
    )

    # todo add phases where manifest gets resolved, run, etc
    for validation_result in run_experiment_validation(
        lims_id,
        experiment_dir,
        manifest,
    ):
        logger.info("Validation result: %s", validation_result)
        put_asset_validation_result(
            client[table_name].validations,
            validation_result,
        )


def get_validation_results(
    client,
    lims_id: str,
    asset_type: str = None,
    table_name: str = "dev",
):
    return get_asset_validation_results(
        client[table_name].validations,
        lims_id,
        asset_type,
    )


def validate_lims_upload(
    client,
    cursor,
    lims_id: str,
    table_name: str = "dev",
):
    results = get_validation_results(client, lims_id, None, table_name)
    validated = validate_lims(
        cursor,
        lims_id,
        results,
    )
    lims_verified = []
    for validation in validated:
        if validation.lims_verified:
            update_asset_validation_result(
                client[table_name].validations,
                lims_id,
                validation.manifest.asset_type,
                {"lims_verified": True},
            )
            lims_verified.append(validation)

    return lims_verified
