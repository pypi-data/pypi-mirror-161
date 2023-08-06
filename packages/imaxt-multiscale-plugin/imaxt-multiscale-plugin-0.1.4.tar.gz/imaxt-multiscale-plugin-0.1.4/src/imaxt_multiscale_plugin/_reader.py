"""
This module is an example of a barebones numpy reader plugin for napari.

It implements the Reader specification, but your plugin may choose to
implement multiple readers or even other plugin contributions. see:
https://napari.org/plugins/guides.html?#readers
"""
from contextlib import suppress
from pathlib import Path

import dask.array as da
import xarray as xr
import zarr

from .utils import get_display_range


def get_store_from_path(path):
    if path.startswith("s3://"):
        from imaxt_image.io.s3 import get_s3_store

        _, alias, instrument, name = Path(path).parts
        store = None
        for extra in ["mos", "mos.zarr"]:  # v0.9 of pipeline
            with suppress(PermissionError):
                store = get_s3_store(name, alias, instrument, extra)
            if store is not None:
                break
    else:
        path = Path(path)
        if (path / "mos").exists():
            store = path / "mos"
        else:
            store = path / "mos.zarr"  # v0.9 of pipeline
    return store


def napari_get_reader(path):
    """A basic implementation of a Reader contribution.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, list):
        # A path list does not make sense for this plugin
        return None

    store = get_store_from_path(path)

    try:
        zarr.open(store, mode="r")
    except zarr.errors.PathNotFoundError:
        return None

    # otherwise we return the *function* that can read ``path``.
    return reader_function


def reader_function(path):
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of
        layer. Both "meta", and "layer_type" are optional. napari will
        default to layer_type=="image" if not provided
    """
    store = get_store_from_path(path)
    ds = xr.open_zarr(store, group="l.16")
    channels = list(ds.channel.values)

    cube = []
    ds = xr.open_zarr(store, group="l.16")
    bscale = 1
    bzero = 0
    p1, p2 = get_display_range(ds["S001"].sel(z=0) * bscale + bzero)
    for group in ["", "l.2", "l.4", "l.8", "l.16"]:
        ds = xr.open_zarr(store, group=group)
        if "type" in ds.coords:  # v0.9 of pipeline
            ds = ds.sel(type="mosaic").astype("float32")
        data = da.stack(
            [
                (ds[s].sel(z=0).data.astype("float32") * bscale + bzero - p1)
                / (p2 - p1)
                * 10000
                for s in list(ds)
            ]
        )
        cube.append(data)

    # optional kwargs for the corresponding viewer.add_* method
    add_kwargs = {
        "multiscale": True,
        "name": [f"C{ch}" for ch in channels],
        "scale": [1, 1, 1],
        "colormap": ["red", "green", "blue", "cyan"],
        "blending": "ADDITIVE",
        "channel_axis": 1,
        "contrast_limits": [0, 30000],
    }

    layer_type = "image"  # optional, default is "image"
    return [(cube, add_kwargs, layer_type)]
