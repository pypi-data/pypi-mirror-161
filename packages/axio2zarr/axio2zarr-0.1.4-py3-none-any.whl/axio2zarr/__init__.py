import logging
import re
import traceback
from contextlib import closing
from pathlib import Path

import click
import dask.array as da
import xarray as xr
from aicspylibczi import CziFile
from distributed import Client, LocalCluster

from .array import cziArray

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


__version__ = "0.1.4"
__author__ = "Eduardo Gonzalez Solares"
__email__ = "E.GonzalezSolares@ast.cam.ac.uk"


def _parse_section(filename):
    fname = filename.name if isinstance(filename, Path) else filename
    s = re.compile(r"(\d+)\)?\.czi").search(fname).groups()[0]
    s = int(s)
    return f"S{s:03d}"


def _get_coords(czi_files: list[Path]):
    x_shape = 1
    y_shape = 1
    m_shape = 1
    c_shape = 1
    s_shape = 1
    for this_file in czi_files:
        czi = CziFile(this_file)
        shape = czi.get_dims_shape()[0]
        x_shape = shape["X"][1] if shape["X"][1] > x_shape else x_shape
        y_shape = shape["Y"][1] if shape["Y"][1] > y_shape else y_shape
        m_shape = shape["M"][1] if shape["M"][1] > m_shape else m_shape
        c_shape = shape["C"][1] if shape["C"][1] > c_shape else c_shape
        s_shape = shape["S"][1] if shape["S"][1] > s_shape else s_shape

    coords = {
        "z": range(s_shape),
        "channel": range(c_shape),
        "tile": range(m_shape),
        "x": range(x_shape),
        "y": range(y_shape),
    }

    return coords


def convert2zarr(input_path: Path, output_path: Path):
    czi_files = [*input_path.glob("*.czi")]
    czi_files.sort(key=_parse_section)

    coords = _get_coords(czi_files)

    # Initialize storage
    ds = xr.Dataset(coords=coords)
    ds.to_zarr(output_path, mode="w")

    attrs = {"orig_name": input_path.name}

    for this_file in czi_files:
        czi = CziFile(this_file)
        czif = cziArray(czi)
        arr = da.from_array(czif, chunks=czif.chunks)
        section_name = _parse_section(this_file.name)
        arrx = xr.DataArray(
            arr, coords=czif.dimensions, attrs=czif.metadata, name=section_name
        )
        ds = xr.Dataset(coords=coords)
        ds[section_name] = arrx
        ds = ds.astype("uint16")
        ds = ds.chunk({"tile": 1, "channel": 1, "z": 1})
        ds.attrs = attrs
        ds.to_zarr(output_path, mode="a")
        logger.info("Processed section %s - %s", section_name, this_file.name)


def axio2zarr(input_path, output_path):
    input_fn = Path(input_path)
    output_fn = Path(output_path) / input_fn.name
    with closing(LocalCluster(processes=False, dashboard_address=None)) as cluster:
        Client(cluster)
        convert2zarr(input_fn, output_fn)
    return f"{output_fn}"


@click.command()
@click.argument("input_path")
@click.argument("output_path")
def main(input_path, output_path):
    try:
        axio2zarr(input_path, output_path)
    except Exception as err:
        print(f"Error: {str(err)}")
        print(f"Details: {traceback.format_exc()}")
