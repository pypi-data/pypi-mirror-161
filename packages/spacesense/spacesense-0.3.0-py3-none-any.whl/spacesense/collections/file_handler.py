import logging
import os
import uuid
from typing import List

logger = logging.getLogger(__name__)


class Raster:
    """Class representing a raster item uploaded by a user from :py:meth:`models`"""

    def __init__(self, file_path: str, name: str = None, bands: list = [], id: str = None):
        """Create an instance of the raster class :py:class:`models`

        Parameters:
            file_path (str): Path to the raster file on the local environment.
            name (str, optional): Give a name to the raster file, which replaces the default file name in the fused result
            bands (list, optional): List of bands from the raster to fuse.
            id (str, optional): A unique ID for the layer.

        By default, when assigning a raster to the Raster class, all bands are selected and fused when passed.
        The following types of raster files are supported:

        - Geotiff (.tif or .tiff)
        - GeoPackage (.gpkg)
        """

        self.type = "raster"
        self.file_path = file_path
        self.bands = bands
        self.name = name or os.path.basename(file_path).split(".")[0]
        self.id = id or str(uuid.uuid4())

    def add_to_request(self, request):
        file = request.files.add()
        file.name = self.name
        file.type = self.type
        file.extension = os.path.basename(self.file_path).split(".")[-1]
        file.data = read_file_as_bytes(os.path.join(self.file_path))
        request.files_options[file.name] = self._compute_attribute_dict()

    def _compute_attribute_dict(self):
        return {"include": self.bands}


class Vector:
    SUPPORTED_EXTENSIONS = [
        "shp",
        "json",
        "geojson",
        "gpkg",
    ]

    def __init__(
        self,
        file_path: str,
        name: str = None,
        interpolation_method: str = None,
        attributes: List[str] = [],
        exclude_attributes: List[str] = [],
        id: str = None,
    ):

        """Create an instance of the vector class :py:class:`models`

        Parameters:
            file_path (str): Path to the vector file on the local environment.
            name (str, optional): Give a name to the vector file, which replaces the default file name in the fused result.
            interpolation_method (str, optional): {‘linear’, ‘nearest’, ‘cubic’} Specify a interpolation method to use when rasterizing the vector file. This option is currently only available for point vector data.
            attributes (list, optional): List of attributes from the vector to fuse.
            exclude_attributes (list, optional): List of attributes to exclude from the fusion. Attributes not in this list will be fused.
            id (str, optional): A unique ID for the layer.

        By default, when assigning a vector to the Vector class, all attributes are selected and fused when passed.
        The following types of vector files are supported:

        - Shapefile (.shp)
        - JSON (.json)
        - GeoJSON (.geojson)
        - GeoPackage (.gpkg)
        """

        if type(attributes) is not list:
            raise ValueError("attributes must be a list")
        if type(exclude_attributes) is not list:
            raise ValueError("exlude_attributes must be a list")
        self.extension = os.path.basename(file_path).split(".")[-1]
        if self.extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError("Uploaded File is not supported", f"Supported types: {self.SUPPORTED_EXTENSIONS}")
        self.type = "vector"
        self.file_path = file_path
        self.interpolation_method = interpolation_method
        self.folder_path = os.path.dirname(self.file_path)
        self.attributes = attributes
        self.exclude_attributes = exclude_attributes
        self.name = name or os.path.basename(file_path).split(".")[0]
        self.id = id or str(uuid.uuid4())

    def add_to_request(self, request):
        if self.extension == "shp":
            for filename in os.listdir(self.folder_path):
                if filename.split(".")[0] == os.path.basename(self.file_path).split(".")[0]:
                    self._add_file_to_request(request, filename)
        else:
            self._add_file_to_request(request, os.path.basename(self.file_path))
        request.files_options[self.name] = self._compute_option_dict()

    def _add_file_to_request(self, request, filename):
        file = request.files.add()
        file.name = self.name
        file.type = self.type
        file.extension = filename.split(".")[-1]
        file.data = read_file_as_bytes(os.path.join(os.path.abspath(self.folder_path), filename))

    def _compute_option_dict(self):
        options = {}
        if self.attributes:
            options["include"] = self.attributes
        if self.exclude_attributes:
            options["exclude"] = self.exclude_attributes
        if self.interpolation_method:
            options["interpolation_method"] = self.interpolation_method
        return options


def read_file_as_bytes(file_path) -> bytes:
    with open(file_path, "rb") as f:
        return f.read()


def read_file_as_chunks(file_path, chunksize=None):
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunksize)
            if chunk:
                for b in chunk:
                    yield b
            else:
                break
