import logging

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from shapely.geometry import Point

logger = logging.getLogger(__name__)


def distance_to_water(ds: xr.Dataset, mine_lon: float, mine_lat: float, plot: bool = True) -> float:
    """
    Function to calculate the distance from a specified longitude and latitude to the nearest water body. The water body is taken from the first index on the Sentinel-2 SCL
    band in the fused result. The function returns the distance in meters, and plots the distance in a circle around the specified location.

    To use this function, you must pass a Sentinel-2 dataset with the SCL band already fused. This dataset must also have been processed through the "utils.add_time_dimension" function
    to ensure consistency. Please ensure that clouds are minimal or nonexistant, as that can impact the location of the water body in the SCL band.
    """

    ds = ds.drop(["time", "spatial_ref"])
    ds["water"] = (ds["s2_SCL"][0] == 6) * 1

    # Polygonize
    x, y, water = ds.x.values, ds.y.values, ds["water"].values
    x, y = np.meshgrid(x, y)
    x, y, water = x.flatten(), y.flatten(), water.flatten()

    wat_pd = pd.DataFrame.from_dict({"water": water, "x": x, "y": y})
    threshold = 0.5
    wat_pd = wat_pd[wat_pd["water"] > threshold]
    wat_vector = gpd.GeoDataFrame(geometry=gpd.GeoSeries.from_xy(wat_pd["x"], wat_pd["y"]), crs="EPSG:4326")
    wat_vector = wat_vector.to_crs("EPSG:3857")
    wat_vector = wat_vector.buffer(5, cap_style=3)
    mine_loc = Point(mine_lon, mine_lat)
    gdf = gpd.GeoDataFrame({"mine": [1], "geometry": [mine_loc]}, crs="EPSG:4326")
    gdf = gdf.to_crs(3857)
    wat_vector = wat_vector.to_crs(3857)
    wat_dist = wat_vector.distance(gdf["geometry"][0])
    min_dist = round(min(wat_dist), 2)
    logger.info(f"Minimal distance to nearest water body: {min_dist} [m]")

    # Plot
    if plot is True:
        fig, ax = plt.subplots(1, 1)
        circle1 = plt.Circle((gdf["geometry"].x, gdf["geometry"].y), min_dist, fill=False)
        ax.add_patch(circle1)
        wat_vector.plot(ax=ax)
        gdf.plot(color="None", edgecolor="red", linewidth=2, zorder=1, ax=ax)
        plt.show()

    return min_dist
