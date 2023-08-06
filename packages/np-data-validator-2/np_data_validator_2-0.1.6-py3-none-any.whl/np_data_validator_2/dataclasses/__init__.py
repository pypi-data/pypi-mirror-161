from typing import Any, Callable, Dict, List, Optional, Tuple

from dataclasses import dataclass, field

from ..builtins import resolve_processor, resolve_validator


def _post_init_dataclass(obj, _dataclass):
    if obj is not None and not isinstance(obj, _dataclass):
        return _dataclass(**obj)
    else:
        return obj


@dataclass
class Processor:

    name: str
    resolved_function: field(init=False) = None
    args: dict = field(default_factory=dict)
    store_result: bool = True

    def __post_init__(self):
        self.resolved_function = resolve_processor(self.name)


@dataclass
class ProcessorResult:

    value: Any
    from_memo: bool = False


@dataclass
class Validator:

    name: str
    resolved_function: field(init=False) = None
    args: dict = field(default_factory=dict)
    processor: Optional[Processor] = None

    def __post_init__(self):
        self.resolved_function = resolve_validator(self.name)
        self.processor = _post_init_dataclass(self.processor, Processor)


@dataclass
class ValidationResult:

    name: str
    args: tuple[Any, dict]
    value: tuple[Any, bool]
    processed: Optional[ProcessorResult] = None

    def __post_init__(self):
        self.processed = _post_init_dataclass(self.processed, ProcessorResult)


@dataclass
class AssetValidationManifest:

    asset_type: str
    glob_pattern: str
    validators: list[Validator]

    def __post_init__(self):
        self.validators = [
            _post_init_dataclass(data, Validator) for data in self.validators
        ]


@dataclass
class AssetValidationResult:

    version: str
    lims_id: str
    experiment_dir: str
    filepath: str
    checksum: str
    lims_verified: bool
    validation: list[ValidationResult]
    manifest: AssetValidationManifest

    def __post_init__(self):
        self.validation = [
            _post_init_dataclass(data, ValidationResult) for data in self.validation
        ]
        self.manifest = _post_init_dataclass(
            self.manifest,
            AssetValidationManifest,
        )


@dataclass
class ValidationManifest:

    name: str
    assets: list[AssetValidationManifest]

    def __post_init__(self):
        self.assets = [
            _post_init_dataclass(data, AssetValidationManifest) for data in self.assets
        ]


# @nested_dataclass
# class ValidationManifestMini:

#     name: str
#     assets: List[AssetValidationManifest]
#     validators: List[Validator] = []
