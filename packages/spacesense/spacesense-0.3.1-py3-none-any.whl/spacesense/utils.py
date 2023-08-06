import datetime

import xarray as xr


def add_time_dimension(dataset):
    """
    Collapse a 2D Xarray Dataset, with each band + date combination as a separate variable, into a 3D Xarray Dataset, with dimensions of x, y, and time.
    The current implementation assumes only bands with the name beginning with "s1" or "s2" have a time dimension. Bands not beginning with those strings (assumed to be custom rasters or vectors)
    are first dropped, then assigned to the final dataset with only x and y dimensions.
    """
    date_coo = []
    other_var = {}
    var_data = {}
    data_variables = {}

    if "spatial_ref" not in dataset.coords:
        dataset = dataset.set_coords(("y", "x", "spatial_ref"))

    for key in dataset.data_vars.keys():
        if not (key.startswith("s2") or key.startswith("s1")):
            other_var[key] = (["y", "x"], dataset[key].to_numpy())
            dataset = dataset.drop(key)

    for key in dataset.data_vars.keys():
        if not (key[:-9] in var_data.keys()):
            var_data[key[:-9]] = []
        if not (datetime.datetime.strptime(key[-8:], "%Y%m%d") in date_coo):
            date_coo.append(datetime.datetime.strptime(key[-8:], "%Y%m%d"))
        var_data[key[:-9]].append(dataset[key].to_numpy())

    for param_nam in var_data.keys():
        data_variables[param_nam] = (["time", "y", "x"], var_data[param_nam])

    data_variables = {**data_variables, **other_var}

    ds = xr.Dataset(
        data_vars=data_variables, coords={"time": date_coo, "y": dataset.y, "x": dataset.x}, attrs=dataset.attrs
    )
    if "nodatavals" in ds.attrs:
        del ds.attrs["nodatavals"]
    if "scales" in ds.attrs:
        del ds.attrs["scales"]
    if "offsets" in ds.attrs:
        del ds.attrs["offsets"]
    if "descriptions" in ds.attrs:
        del ds.attrs["descriptions"]
    return ds
