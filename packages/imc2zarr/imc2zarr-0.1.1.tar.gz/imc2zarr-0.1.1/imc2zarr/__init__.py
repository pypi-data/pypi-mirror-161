import traceback
from pathlib import Path

import click

from .converter import Imc2Zarr

__version__ = "0.1.1"
__author__ = "Mo Alsad and Eduardo Gonzalez Solares"
__email__ = "msa51@cam.ac.uk"
_credits__ = [
    "Mo Alsad",
    "Eduardo Gonzalez Solares",
    "Vito Zanotelli",
    "Anton Rau",
    "Jonas Windhager"
]


def imc2zarr(input_path: Path, output_path: Path):
    imc2zarr_converter = Imc2Zarr(input_path, output_path)
    imc2zarr_converter.convert()
    return imc2zarr_converter.output_fn


@click.command()
@click.argument("input_path")
@click.argument("output_path")
def main(input_path, output_path):
    try:
        imc2zarr(input_path, output_path)
    except Exception as err:
        print("Error: {}".format(str(err)))
        print("Details: {}".format(traceback.format_exc()))
