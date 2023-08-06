# type: ignore[attr-defined]
from typing import Literal, Optional

from enum import Enum
from random import choice

import typer
from psycopg import connect
from pymongo import MongoClient
from rich.console import Console

from np_data_validator_2 import version
from np_data_validator_2.core import (
    create_validation_manifest_from_json,
    get_validation_results,
    validate_lims,
    validate_local_experiment,
)
from np_data_validator_2.transformers import from_AssetValidationResult

app = typer.Typer(
    name="np_data_validator_2",
    help="Awesome `np_data_validator_2` is a Python cli/package created with https://github.com/TezRomacH/python-package-template",
    add_completion=False,
)
console = Console()


def version_callback(print_version: bool) -> None:
    """Print the version of the package."""
    if print_version:
        console.print(
            f"[yellow]np_data_validator_2[/] version: [bold blue]{version}[/]"
        )
        raise typer.Exit()


@app.command(name="")
def main(
    print_version: bool = typer.Option(
        None,
        "-v",
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Prints the version of the np_data_validator_2 package.",
    ),
) -> None:
    """Prints version"""


@app.command()
def create_manifest(
    db_address: str,
    json_path: str,
) -> None:
    create_validation_manifest_from_json(
        MongoClient(db_address),
        json_path,
        "dev",
    )
    console.print("Created manifest!")


@app.command()
def validate_local(
    db_address: str,
    lims_id: str,
    name: str,
    experiment_dir: str,
) -> None:
    client = MongoClient(db_address)
    validate_local_experiment(
        client,
        lims_id,
        name,
        experiment_dir,
        "dev",
    )


@app.command()
def validate_lims(
    db_address: str,
    lims_address: str,  # postgres://limsreader:limsro2@limsdb2:5432/lims2
    lims_id: str,
) -> None:
    client = MongoClient(db_address)
    conn = connect(**psycopg.conninfo.conninfo_to_dict(lims_address))
    with conn.cursor() as cursor:
        validated = validate_lims_upload(
            client,
            cursor,
            lims_id,
        )
    console.print(from_AssetValidationResult(validation) for validation in validations)


@app.command()
def validations(
    db_address: str,
    lims_id: str,
) -> None:
    client = MongoClient(db_address)
    validations = get_validation_results(
        client,
        lims_id,
        "dev",
    )
    if not len(validations) > 0:
        console.print("No validations found for lims_id=%s" % lims_id)
        return

    console.print("Found validations:")
    for validation in validations:
        console.print(from_AssetValidationResult(validation))


if __name__ == "__main__":
    app()
