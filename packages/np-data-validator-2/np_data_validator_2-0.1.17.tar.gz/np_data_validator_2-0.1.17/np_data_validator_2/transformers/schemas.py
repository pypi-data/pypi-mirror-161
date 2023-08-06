from marshmallow import Schema, fields, post_load, validate

from .. import dataclasses
from ..builtins import get_processor_names, get_validator_names


class Processor(Schema):

    name = fields.Str(validate=validate.OneOf(get_processor_names()))
    args = fields.Dict()
    store_result = fields.Boolean()

    @post_load
    def load(self, data, **kwargs):
        return dataclasses.Processor(**data)


class Validator(Schema):

    name = fields.Str(validate=validate.OneOf(get_validator_names()))
    args = fields.Dict()
    processor = fields.Nested(Processor, allow_none=True, required=False)

    @post_load
    def load(self, data, **kwargs):
        return dataclasses.Validator(**data)


class ProcessorResult(Schema):

    value = fields.Raw()
    from_memo = fields.Boolean()

    @post_load
    def load(self, data, **kwargs):
        return dataclasses.ProcessorResult(**data)


class ValidationResult(Schema):

    name = fields.Str(validate=validate.OneOf(get_validator_names()))
    args = fields.Tuple(
        (
            fields.Raw(allow_none=True),
            fields.Dict(),
        )
    )
    value = fields.Tuple(
        (
            fields.Raw(allow_none=True),
            fields.Boolean(),
        )
    )
    processed = fields.Nested(ProcessorResult, allow_none=True, required=False)

    @post_load
    def load(self, data, **kwargs):
        return dataclasses.ValidationResult(**data)


class AssetValidationManifest(Schema):

    asset_type = fields.Str()
    glob_pattern = fields.Str()
    validators = fields.Nested(Validator, many=True)

    @post_load
    def load(self, data, **kwargs):
        return dataclasses.AssetValidationManifest(**data)


class AssetValidationResult(Schema):

    version = fields.Str()
    lims_id = fields.Str()
    experiment_dir = fields.Str()
    filepath = fields.Str()
    checksum = fields.Str()
    lims_verified = fields.Boolean()
    validation = fields.Nested(ValidationResult, many=True)
    manifest = fields.Nested(AssetValidationManifest)

    @post_load
    def load(self, data, **kwargs):
        return dataclasses.AssetValidationResult(**data)


class ValidationManifest(Schema):

    name = fields.Str()
    assets = fields.Nested(AssetValidationManifest, many=True)

    @post_load
    def load(self, data, **kwargs):
        return dataclasses.ValidationManifest(**data)
