from .dataclasses import AssetValidationResult, ValidationManifest
from .transformers import (
    from_AssetValidationResult,
    from_ValidationManifest,
    to_AssetValidationResult,
    to_ValidationManifest,
)


def get_validation_manifest(table, name: str) -> ValidationManifest:
    data = table.find_one({"name": name}, {"_id": False})
    return to_ValidationManifest(data)


def put_validation_manifest(table, manifest: ValidationManifest):
    return table.insert_one(from_ValidationManifest(manifest))


def get_asset_validation_results(table, lims_id: str) -> AssetValidationResult:
    data = table.find({"lims_id": lims_id}, {"_id": False})
    return [to_AssetValidationResult(doc) for doc in data]


def put_asset_validation_result(table, result: AssetValidationResult):
    return table.insert_one(from_AssetValidationResult(result))


def update_asset_validation_result(table, lims_id: str, name: str, updates: dict):
    return table.update_one(
        {
            "lims_id": lims_id,
            "manifest.asset_type": name,
        },
        {
            "$set": updates,
        },
    )
