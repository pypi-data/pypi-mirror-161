from enum import Enum

import pandas as pd
from satstac import Collection, ItemCollection


class Sentinel1Band(Enum):
    """
    Sentinel-1 bands
    """

    VH = "VH"
    VV = "VV"
    LIA = "LIA"
    MASK = "MASK"


class Sentinel2Band(Enum):
    """
    Sentinel-2 bands
    """

    B01 = "B01"
    B02 = "B02"
    B03 = "B03"
    B04 = "B04"
    B05 = "B05"
    B06 = "B06"
    B07 = "B07"
    B08 = "B08"
    B8A = "B8A"
    B09 = "B09"
    B11 = "B11"
    B12 = "B12"
    SCL = "SCL"
    CLOUD_SHADOWS = "CLOUD_SHADOWS"
    CLOUD_HIGH_PROBABILITY = "CLOUD_HIGH_PROBABILITY"


class Sentinel1:
    bands = [b.value for b in Sentinel1Band]


class Sentinel2:
    bands = [b.value for b in Sentinel2Band]


class Sentinel1SearchResult:
    def __init__(self, aoi, data_coverage, dataframe, ok: bool = True, reason: str = None):
        """
        Create an instance of the Sentinel-1 Search Result class :py:class:`models

        Attributes:
            aoi (str): A GeoJSON polygon
            output_bands (str, optional): List of strings specifying the names of output bands from the following list of Sentinel-1 bands. By default, all bands are selected and fused. \n
                - VV
                - VH
                - LIA
                - MASK

        To learn more about SAR polarization (VV and VH) and LIA, please review the SAR basics page on the left hand side.

        Pre-processing steps are applied to the level 1 S1 data at this stage through the Snappy Graph Processing Framework (GPF) tool. Given here are the processing steps, and the GPF parameters used.

        | 1. Border noise removal
        |   GPF “Remove-GRD-Border-Noise” process set to True, with the “borderLimit” set to 2000, and the “trimThreshold” set to 0.5
        | 2. Thermal noise removal
        |   GPF “removeThermalNoise” process set to True
        | 3. Radiometric calibration
        |   GPF "outputSigmaBand" set to True, and "outputImageScaleInDb" set to False
        | 4. Terrain correction
        |    GPF options of:
        |        “demName" set to "SRTM 3Sec"
        |        "demResamplingMethod" set to "BILINEAR_INTERPOLATION"
        |        "imgResamplingMethod" set to "BILINEAR_INTERPOLATION"
        |        ”saveProjectedLocalIncidenceAngle" set to True
        |        "saveSelectedSourceBand" set to True
        |        "pixelSpacingInMeter" set to “resolution”)
        |        "alignToStandardGrid" set to True)
        |        "standardGridOriginX" and "standardGridOriginY" set to 0
        |    The “mapProjection” was set using the following projection:
        |        proj = (
        |        'GEOGCS["WGS84(DD)",'
        |        'DATUM["WGS84",'
        |        'SPHEROID["WGS84", 6378137.0, 298.257223563]],'
        |        'PRIMEM["Greenwich", 0.0],'
        |        'UNIT["degree", 0.017453292519943295],'
        |        'AXIS["Geodetic longitude", EAST],'
        |        'AXIS["Geodetic latitude", NORTH]]'
        |        )

        """
        self.ok = ok
        self.reason = reason
        self.aoi = aoi
        self.data_coverage = data_coverage
        self.dataframe = dataframe
        if self.dataframe is not None and not self.dataframe.empty:
            self.dataframe["date"] = pd.to_datetime(self.dataframe["date"])
        self.output_bands = Sentinel1.bands

    def has_results(self):
        return self.dataframe is not None and len(self.dataframe) > 0

    @property
    def output_bands(self):
        return self._output_bands

    @output_bands.setter
    def output_bands(self, bands: list):
        unknown_bands = []
        for b in bands:
            if b.upper() not in Sentinel1.bands:
                unknown_bands.append(b)
            self._output_bands = [b.upper() for b in bands]
        if unknown_bands:
            raise ValueError(f"Not recognised as band name: {unknown_bands}")

    @property
    def to_dict(self):
        return self.dataframe.to_dict(orient="records")

    @staticmethod
    def concat(search_results):
        if not search_results:
            raise ValueError("Nothing to concat")
        first_item = search_results[0]
        dataframe = pd.concat([search_result.dataframe for search_result in search_results])
        return Sentinel1SearchResult(first_item.aoi, first_item.data_coverage, dataframe)


class Sentinel2SearchResult:
    def __init__(self, aoi, item_collection: ItemCollection, ok: bool = True, reason: str = None):
        """
        Create an instance of the Sentinel-2 Search Result class :py:class:`models.

        Attributes:
            aoi (str): A GeoJSON polygon
            output_bands (str, optional): List of strings specifying the names of output bands from the following list of Sentinel-2 bands.

        By default, only B02, B03, B04, B08, and the SCL bands are selected and fused. If overwriting the default bands, the fused result
        will keep the order specified in the "output_bands" command.\n
                - B01
                - B02
                - B03
                - B04
                - B05
                - B06
                - B07
                - B08
                - B08a
                - B09
                - B11
                - B12
                - SCL
                - CLOUD_SHADOWS
                - CLOUD_HIGH_PROBABILITY

        The Sentinel-2 data retrieved is L2A, meaning it represents the bottom of the atmosphere (BOA) reflectance values.
        The following table presents some basic information about the available S2 bands:

        +------------+------------+---------------------+--------------------------------------+
        | Band	     | Resolution | Central Wavelength  |Description                           |
        +============+============+=====================+======================================+
        | B01        | 60 m       | 443 nm              | Ultra Blue (Coastal and Aerosol)     |
        +------------+------------+---------------------+--------------------------------------+
        | B02        | 10 m       | 490 nm              | Blue                                 |
        +------------+------------+---------------------+--------------------------------------+
        | B03        | 10 m       | 560 nm              | Green                                |
        +------------+------------+---------------------+--------------------------------------+
        | B04        | 10 m       | 665 nm              | Red                                  |
        +------------+------------+---------------------+--------------------------------------+
        | B05        | 20 m       | 705 nm              | Visible and Near Infrared (VNIR)     |
        +------------+------------+---------------------+--------------------------------------+
        | B06        | 20 m       | 740 nm              | Visible and Near Infrared (VNIR)     |
        +------------+------------+---------------------+--------------------------------------+
        | B07        | 20 m       | 783 nm              | Visible and Near Infrared (VNIR)     |
        +------------+------------+---------------------+--------------------------------------+
        | B08        | 10 m       | 842 nm              | Visible and Near Infrared (VNIR)     |
        +------------+------------+---------------------+--------------------------------------+
        | B8a        | 20 m       | 865 nm              | Visible and Near Infrared (VNIR)     |
        +------------+------------+---------------------+--------------------------------------+
        | B09        | 60 m       | 940 nm              | Short Wave Infrared (SWIR)           |
        +------------+------------+---------------------+--------------------------------------+
        | B11        | 20 m       | 1610 nm             | Short Wave Infrared (SWIR)           |
        +------------+------------+---------------------+--------------------------------------+
        | B12        | 20 m       | 2190 nm             | Short Wave Infrared (SWIR)           |
        +------------+------------+---------------------+--------------------------------------+

        To learn more about Sentinel-2 bands, their details, and their uses, `this page <https://gisgeography.com/sentinel-2-bands-combinations/>`_ has many resources available.

        SCL or Scene Classification Layer, aims to provide pixel classification maps of clouds, cloud shadows,
        vegetation, soils/deserts, water, and snow, as well as defective, saturated, no data, or unclassified values. For more information about Sentinel-2's SCL band, please visit
        `this page describing the Sentinel-2 algorithm <https://sentinels.copernicus.eu/web/sentinel/technical-guides/sentinel-2-msi/level-2a/algorithm/>`_.

        Please note, Band 10 is not available for level 2A Sentinel-2 data, as this band is used for atmospheric corrections only.

        The following Sentinel-2 properties are available in the S2 search result:

        - id
        - date
        - tile
        - valid_pixel_percentage
        - platform
        - relative_orbit_number
        - product_id
        - datetime
        - swath_coverage_percentage
        - no_data*
        - cloud_shadows*
        - vegetation*
        - not_vegetated*
        - water*
        - cloud_medium_probability*
        - cloud_high_probability*
        - thin_cirrus*
        - snow*

        **swath_coverage_percentage** is simply the percetage of data covered by the Sentinel-2 swath at the AOI level.

        **valid_pixel_percentage** is defined as a combination of pixels, at the AOI level, NOT classified as no_data,
        cloud_shadows, cloud_medium_probability, cloud_high_probability, and snow.
        This is a very useful property to use when determining if a Sentinel-2 scene clear of clouds and snow for vegetation and infrastructure monitoring.

        **"*"** denotes that the property is a direct calculation of the percent coverage of the associated SCL bands over the AOI.

        """
        self.ok = ok
        self.reason = reason
        self.aoi = aoi
        self._item_collection = item_collection
        if item_collection:
            self._dataframe = self.metadata_dataframe_from_item_collection(item_collection)
        self.output_bands = ["B02", "B03", "B04", "B08", "SCL"]

    def has_results(self):
        return self.dataframe is not None and len(self.dataframe) > 0

    @property
    def output_bands(self):
        return self._output_bands

    @property
    def count(self):
        return len(self._item_collection._items)

    @output_bands.setter
    def output_bands(self, bands: list):
        self._output_bands = [b.upper() for b in bands]

    @property
    def dataframe(self):
        return self._dataframe

    @dataframe.setter
    def dataframe(self, dataframe: pd.DataFrame):
        if type(dataframe) != pd.DataFrame:
            raise ValueError("dataframe should be a pandas.DataFrame")
        self._dataframe = dataframe
        self._item_collection = self.item_collection_from_metadata_dataframe()

    @property
    def item_collection(self):
        return self._item_collection

    @item_collection.setter
    def item_collection(self, item_collection: ItemCollection):
        if type(item_collection) != ItemCollection:
            raise ValueError("item_collection should be an ItemCollection")
        self._item_collection = item_collection
        self._dataframe = self.metadata_dataframe_from_item_collection()

    @property
    def to_dict(self):
        return self._item_collection.geojson()

    def metadata_dataframe_from_item_collection(self, item_collection: ItemCollection = None) -> pd.DataFrame:
        item_collection = item_collection or self._item_collection
        meta = [item.properties["spacesense"] for item in item_collection]
        columns = [
            "id",
            "date",
            "tile",
            "valid_pixel_percentage",
            "platform",
            "relative_orbit_number",
            "product_id",
            "datetime",
            "swath_coverage_percentage",
            "no_data",
            "cloud_shadows",
            "vegetation",
            "not_vegetated",
            "water",
            "cloud_medium_probability",
            "cloud_high_probability",
            "thin_cirrus",
            "snow",
        ]
        df = pd.DataFrame(data=meta, columns=columns)
        df = df.sort_values(["date"], ascending=True)
        df["date"] = pd.to_datetime(df["date"])
        return df

    def item_collection_from_metadata_dataframe(self):
        ids = list(self._dataframe.id)
        self._item_collection._items = [item for item in self._item_collection._items if item.id in ids]
        return self._item_collection

    @staticmethod
    def concat(search_results):
        if not search_results:
            raise ValueError("Nothing to concat")
        first_item = search_results[0]
        items = []
        collections = []
        for search_result in search_results:
            items.extend(search_result.item_collection._items)
            collections.extend(
                [Collection(collection) for collection in search_result.item_collection.geojson()["collections"]]
            )

        result = Sentinel2SearchResult(first_item.aoi, ItemCollection(items, collections))
        return result

    def filter_duplicate_dates(self):
        """
        Finds any duplicate dates with the S2 search result and drops (filters) the duplicate item with the lowest valid_pixel_percentage (if different).
        If valid_pixel_percentage is the same in both results, the item that comes first in the dataframe index is dropped.
        """
        date_counts = self._dataframe.date.value_counts()
        for i in enumerate(date_counts):
            if i[1] > 1:
                dupe = self._dataframe[self._dataframe.date == date_counts.index[i[0]]]
                if dupe.valid_pixel_percentage.iloc[0] > dupe.valid_pixel_percentage.iloc[1]:
                    self._dataframe = self._dataframe.drop(dupe.valid_pixel_percentage.index[1])
                else:
                    self._dataframe = self._dataframe.drop(dupe.valid_pixel_percentage.index[0])
