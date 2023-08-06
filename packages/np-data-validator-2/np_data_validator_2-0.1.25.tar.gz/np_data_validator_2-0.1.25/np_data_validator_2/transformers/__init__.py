from ..dataclasses import AssetValidationResult, ValidationManifest
from . import schemas

validation_plan_schema = schemas.ValidationManifest()
asset_validation_result_schema = schemas.AssetValidationResult()


def from_ValidationManifest(
    value: ValidationManifest,
) -> dict:
    return validation_plan_schema.dump(value)


def to_ValidationManifest(
    value: dict,
) -> ValidationManifest:
    return validation_plan_schema.load(value, unknown="exclude")


def from_AssetValidationResult(
    value: AssetValidationResult,
) -> dict:
    return asset_validation_result_schema.dump(value)


def to_AssetValidationResult(
    value: dict,
) -> AssetValidationResult:
    return asset_validation_result_schema.load(value, unknown="exclude")
