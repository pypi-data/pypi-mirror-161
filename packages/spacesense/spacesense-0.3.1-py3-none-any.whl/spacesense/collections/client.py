"""
client.py
====================================
All classes necessary to use SpaceSense library.
"""
import datetime
import json
import logging
import os
import uuid
from tempfile import NamedTemporaryFile
from typing import Any, Dict, List, Union

import grpc
import pandas as pd
import xarray as xr
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Struct
from pandas.core.frame import DataFrame
from rasterio.io import MemoryFile
from satstac import Collection, Item, ItemCollection
from xarray.core.dataset import Dataset

from spacesense import config
from spacesense.collections.file_handler import Raster, Vector
from spacesense.collections.models import Sentinel1SearchResult, Sentinel2SearchResult
from spacesense.common.proto.backend import backend_pb2, backend_pb2_grpc

logger = logging.getLogger(__name__)


class GrpcAuth(grpc.AuthMetadataPlugin):
    def __init__(self, key):
        self._key = key

    def __call__(self, context, callback):
        callback((("rpc-auth-header", self._key),), None)


class Sentinel1ResultItem:
    """Class representing one result item from :py:meth:`Client.compute_ard`"""

    def __init__(self, date, status, data=None, reason=None, file_path=None, bucket_path=None):
        """Create an instance of the :py:class:`Client.Sentinel1ResultItem`"""
        self.date = date
        self.status = status
        self.scene_metadata = None
        self._data = data
        self.file_path = file_path
        self.reason = reason
        self.bucket_path = bucket_path
        self.data = None
        if self.file_path:
            self._init_from_local_file()
        elif self._data and len(self._data) > 0:
            with MemoryFile(self._data) as mem_file:
                # xr.open_rasterio is deprecated
                # but we can't use xr.open_dataset(mem_file.name, engine="rasterio") or rio.open_rasterio(os.path.join(user_files[0].file_path))
                # because currently we lose the geotiff "scene_metadata"
                data_array = xr.open_rasterio(mem_file.name)
                self.data = self._redesign_to_dataset(data_array)

    def _init_from_local_file(self):
        # xr.open_rasterio is deprecated
        # but we can't use xr.open_dataset(mem_file.name, engine="rasterio") or rio.open_rasterio(os.path.join(user_files[0].file_path))
        # because currently we lose the geotiff "scene_metadata"
        data_array = xr.open_rasterio(self.file_path)
        # init date
        self.date = datetime.datetime.strptime(data_array.attrs["TIFFTAG_DATETIME"], "%Y:%m:%d %H:%M:%S")

        # init scene metadata
        scene_metadata_list = list(eval(data_array.attrs["scene_metadata"]))
        scene_metadata_with_date = []
        for scene_metadata in scene_metadata_list:
            scene_metadata_copy = {"date": self.date}
            scene_metadata_copy.update(scene_metadata)
            scene_metadata_with_date.append(scene_metadata_copy)
        self.scene_metadata = scene_metadata_with_date

        # redesign dataset to
        self.data = self._redesign_to_dataset(data_array)

    def _redesign_to_dataset(self, data_array: xr.DataArray) -> Dataset:
        """Reformat the metadata from the geotiff to a dict"""
        data_array.attrs["scene_metadata"] = self.scene_metadata
        data_array.coords["time"] = self.date
        # Create a dataset by splitting bands into separate variables
        dataset = data_array.to_dataset(dim="band", promote_attrs=True)
        # Rename data variables into more relevant name
        dataset = dataset.rename_vars({1: "vh", 2: "vv", 3: "lia", 4: "mask"})
        return dataset

    def __str__(self):
        """Returns a formated representation of the result Item"""
        return f"date={self.date}, status={self.status}, file_path={self.file_path}"

    @property
    def processing_status(self) -> dict:
        """Returns information about the processing status"""
        return {
            "date": self.date,
            "status": self.status,
            "reason": self.reason,
            "file_path": self.file_path,
        }


class Sentinel1Result:
    """Class containing the result of :py:meth:`Client.compute_ard`

    Attributes:
        ok (bool): :py:attr:`Sentinel1Result.ok` is True when :py:meth:`Client.compute_ard` returns usable data, False otherwise.
        reason (str, None): Provides additional information when :py:attr:`Sentinel1Result.ok` is false and result is not accessible. if :py:attr:`Sentinel1Result.ok` is True, :py:attr:`Sentinel1Result.reason` will be None.
        items (list): List contraining :py:class:`Sentinel1ResultItem`
    """

    def __init__(self, items: List[Sentinel1ResultItem] = None, ok=True, reason=None):
        self.ok: bool = ok
        self.reason: str = reason
        self._items = items if items is not None else []
        self._items.sort(key=lambda x: x.date)
        self._scene_metadata = None
        self._dataset = None
        self._status = None

    @property
    def status(self) -> DataFrame:
        """Returns the status for each scene as a DataFrame

        Returns:
            DataFrame containing the status for each scene.

        Raise:
            RuntimeError: Result not OK. when :py:attr:`Sentinel1Result.ok` is False
        """
        if not self.ok:
            raise RuntimeError("Result not OK")
        if self._status is None:
            self._compute_status()
        return self._status

    @property
    def dataset(self) -> Dataset:
        """Returns a Dataset containing all the Items.

        Returns:
            Dataset containing all the Items.

        Raise:
            RuntimeError: Result not OK. when :py:attr:`Sentinel1Result.ok` is False
        """
        if not self.ok:
            raise RuntimeError("Result not OK")
        if not self._dataset:
            self._compute_dataset()
        return self._dataset

    def _compute_dataset(self):
        self._dataset = xr.concat([item.data for item in self._items], dim="time").sortby("time")

    def _compute_status(self):
        self._status = pd.DataFrame.from_dict([item.processing_status for item in self._items], orient="columns")

    @property
    def scene_metadata(self) -> pd.DataFrame:
        """Returns the metadata for each scene as a Dataframe

        Args:
            returns the scene metadata.

        Returns:
            pd.DataFrame containing the scene metadata as dictionary for each available scenes.
        """
        if not self._scene_metadata:
            scene_metadata_with_date = []
            for item in self._items:
                date_metadata = item.scene_metadata
                scene_metadata_with_date.extend(iter(date_metadata))
            self._scene_metadata = pd.DataFrame.from_dict(scene_metadata_with_date, orient="columns")
        return self._scene_metadata


class FuseResult:
    """Class containing the result of :py:meth:`Client.fuse`"""

    def __init__(
        self, ok=True, reason=None, status=None, data=None, file_path=None, base_dir=None, client_id=None, fuse_id=None
    ):
        self.ok: bool = ok
        self.reason: str = reason
        self.status = status
        self._data = data
        self.file_path = file_path
        self.base_dir = base_dir
        self.client_id = client_id
        self.fuse_id = fuse_id
        self.output_dir = os.path.join(self.base_dir, self.client_id)
        self.filename = self.fuse_id if self.fuse_id else self.client_id
        self._nc_path = os.path.join(self.output_dir, self.filename + ".nc")
        self._geotiff_path = os.path.join(self.output_dir, self.filename + ".tif")

        if self.file_path:
            self._init_from_local_file()
        elif self._data and len(self._data) > 0:
            with NamedTemporaryFile(suffix=".nc") as tempfile:
                tempfile.write(self._data)
                dataset = xr.open_dataset(tempfile.name, decode_coords="all", engine="netcdf4")
                if dataset.attrs.get("additional_info"):
                    dataset.attrs["additional_info"] = eval(dataset.attrs["additional_info"])
            self.dataset = dataset

    def _init_from_local_file(self):
        with xr.open_dataset(self.file_path, decode_coords="all", engine="netcdf4") as ds:
            dataset = ds.load()
        if dataset.attrs.get("additional_info"):
            dataset.attrs["additional_info"] = eval(dataset.attrs["additional_info"])
        self.dataset = dataset

    def __str__(self):
        """Returns a formated representation of the result Item"""
        return f"ok={self.ok}, status={self.status}, data={len(self.data)}, file_path={self.file_path}"

    def to_geotiff(self, file_path: str = None):
        """Save the result to a geotiff file"""
        # Save to geotiff
        if file_path is None:
            file_path = self._geotiff_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.dataset.rio.to_raster(file_path)
        return file_path

    def to_netcdf(self, file_path: str = None):
        """Save the result to a netcdf file"""
        # Save to netcdf
        if file_path is None:
            file_path = self._nc_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.dataset.attrs["additional_info"] = json.dumps(self.dataset.attrs.get("additional_info"))
        self.dataset.to_netcdf(file_path)
        self.dataset.attrs["additional_info"] = eval(self.dataset.attrs["additional_info"])
        return file_path


class Client:
    """Class that allows you to interact with SpaceSense backend."""

    def __init__(self, id=None, backend_url=None):
        """Create an instance of the :py:class:`Client`

        Args:
            id (str, optional): unique id of your compute instance. If not specified, automatically generates a unique ID
        """
        self.backend_url = backend_url or config.BACKEND_URL

        self.api_key = os.environ.get("SS_API_KEY")
        if not self.api_key:
            raise ValueError("Could not find SpaceSense API in SS_API_KEY environment variable.")
        self.id = id or str(uuid.uuid4())
        self.local_output_path = "./generated"
        self.save_to_local = False
        self.save_to_bucket = False
        self.output_crs = None
        self.output_resolution = None

    def set_output_crs(self, output_crs):
        """Set the desired output CRS.

        set :py:attr:`self.output_crs` to a specified `EPSG code`_ as an int.
        :py:attr:`self.output_crs` will define the EPSG of the output returned by :py:meth:`Client.compute_ard` and :py:meth:`Client.fuse`

        Args:
            output_crs (int): Desired output CRS number. By default the value 4326 is used.

        Examples:
            >>> client = Client()
            >>> client.set_output_crs(3857)
            >>> output = client.compute_ard(aoi, start_date, end_date)
            output data will be in EPSG: 3857 instead of the default 4326

        .. _EPSG code:
            https://epsg.io/
        """
        self.output_crs = output_crs

    def set_output_resolution(self, resolution):
        """Set the desired output resolution.

        The Interferometric Wide swath (IW) mode of level 1 Ground Range Detected (GRD) data is used for Sentinel-1 retrievals.
        Level 2A, atmospherically corrected data is used for Sentinel-2 retrievals. Both of these S1 and S2 native pixel resolutions are at 10m²/pixel.
        Please keep these native resolution in mind when up or downscaling the output ARD resolution.

        set :py:attr:`self.output_resolution` to a specified output resolution in meters²/pixel. Default value is 10m²/pixel.
        :py:attr:`self.output_resolution` will define the resolution of the output returned by :py:meth:`Client.compute_ard` and :py:meth:`Client.fuse`

        Args:
            resolution (int): desired output resolution.

        Examples:
            >>> client = Client()
            >>> client.set_output_resolution(8)
            >>> output = client.compute_ard(aoi, start_date, end_date)
            output data resolution will be 8 meters²/pixel

        """
        self.output_resolution = resolution

    def _enable_bucket_output(self, bucket_output_path):
        """Enables the save to bucket option.

        sets :py:attr:`self.save_to_bucket` to True
        and sets :py:attr:`self.bucket_output_path` to the specified bucket path string.
        The output of compute_ard will be saved in the specified bucket.

        Args:
            bucket_output_path (str): Public bucket path,
        Note:
            the :py:attr:`self.bucket_output_path` should be a valid bucket path as a string. it should be accessible in order for the data to be saved.

        """
        self.save_to_bucket = True
        self.bucket_output_path = bucket_output_path

    def _disable_bucket_output(self):
        """Disables the save to bucket option.

        sets :py:attr:`self.save_to_bucket` to False
        The output will no longer be saved in the specified bucket
        """
        self.save_to_bucket = False

    def enable_local_output(self, local_output_path="./generated"):
        """Enables the local output option. Saves the fused result to a netCDF file in the ./generated folder with the client ID
        as a sub-directory.

        sets :py:attr:`self.save_to_local` to True
        and sets :py:attr:`self.local_output_path` to the desired local output path string.
        The output will be saved in the specified directory.

        Args:
            local_output_path (str): path to local directory. By default ./generated

        Examples:
            >>> client = Client()
            >>> client.enable_local_output()
            >>> output = client.compute_ard(aoi, start_date, end_date)
            compute_ard() will save the result and metadata in the ./generated folder

        """
        self.save_to_local = True
        self.local_output_path = local_output_path

    def disable_local_output(self):
        """Disables the local output option.

        sets :py:attr:`self.save_to_local` to False
        The output will no longer be saved in the specified local directory.

        Examples:
            >>> client = Client()
            >>> client.enable_local_output()
            >>> client.disable_local_output()
            >>> output = client.compute_ard(aoi, start_date, end_date)
            results will be returned as a :py:class:`Sentinel1Result`.
        """
        self.save_to_local = False

    def s1_search(self, aoi, start_date, end_date, query_filters=dict(), data_coverage=100) -> Sentinel1SearchResult:
        """
        Search for Sentinel-1 scenes in a given area of interest.

        :param aoi: A GeoJSON polygon
        :param start_date: Start date of the search
        :param end_date: End date of the search
        :param query_filters: A list of filters to apply to the search
        :param data_coverage: Data coverage of the search
        :return: A list of scenes for each date

        The result of s1_search is a pandas dataframe listing the scenes for your aoi and dates. To refine this search,
        simply select the scenes provided in the dataframe using pandas to set as a new (or overwritten) search result variable. This new result can then
        be passed to the fuse fuction.

        If only one date is needed, the start_date and end_date can be equal.
        """

        aoi_param = Struct()
        aoi_param.update(aoi)

        if type(start_date) == str:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()

        if type(start_date) != datetime.date:
            raise ValueError("Invalid start_date, should be a datetime.date object or a str in isoformat")

        if type(end_date) == str:
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

        if type(end_date) != datetime.date:
            raise ValueError("Invalid end_date, should be a datetime.date object or a str in isoformat")

        if start_date == end_date:
            end_date = end_date + datetime.timedelta(days=1)
            logger.warning("start_date and end_date are the same, adding 1 day to end_date")

        query_filter_struct = Struct()
        if query_filters is not None:
            query_filter_struct.update(query_filters)

        filtering_options = Struct()
        filtering_options.update({"data_coverage": data_coverage})

        # Allow to transfer up to 500mo as grpc message
        channel_opt = [
            ("grpc.max_send_message_length", config.GRPC_MAX_SEND_MESSAGE_LENGTH),
            ("grpc.max_receive_message_length", config.GRPC_MAX_RECEIVE_MESSAGE_LENGTH),
        ]
        # with grpc.insecure_channel(config.BACKEND_URL, options=channel_opt,) as channel:

        with grpc.secure_channel(
            self.backend_url,
            grpc.composite_channel_credentials(
                grpc.ssl_channel_credentials(config.CERT), grpc.metadata_call_credentials(GrpcAuth(self.api_key))
            ),
            options=channel_opt,
        ) as channel:
            stub = backend_pb2_grpc.BackendStub(channel)
            try:
                response = stub.GetS1Search(
                    backend_pb2.GetS1SearchRequest(
                        id=self.id,
                        aoi=aoi_param,
                        start_date=start_date.isoformat(),
                        end_date=end_date.isoformat(),
                        sentinel_filtering_options=query_filter_struct,
                        filtering_options=filtering_options,
                    )
                )
                scene_list = create_scene_list_object(response.scenes)
                return Sentinel1SearchResult(aoi, data_coverage, dataframe=pd.DataFrame(data=scene_list))
            except grpc.RpcError as e:
                logger.warning(e.details())
                return Sentinel1SearchResult(aoi, data_coverage=None, dataframe=None, ok=False, reason=e.details())

    # Synchronous version
    def compute_s1_ard(
        self,
        aoi: Any,
        start_date: Union[str, datetime.date],
        end_date: Union[str, datetime.date],
        output_resolution: int = None,
        output_crs: int = None,
        data_coverage=100,
    ) -> Sentinel1Result:
        """Compute sentinel 1 ARD using the specified options.

        This method computes Sentinel 1 data for the specified area and time of interest.
        You can use the other methods of the :py:class:`Sentinel1` in order to customize the behavior of this method.

        Args:
            aoi (dict): geojson feature or feature collection dictionary containing a polygon.
            start_date (Union[str, datetime.date]): defines the computation start date
            end_date (Union[str, datetime.date]): defines the computation end date
            data_coverage (int): Minimum required cover percentage.(by default 100% of coverage is required)

        Returns:
            :py:class:`Sentinel1Result` :py:attr:`Sentinel1Result.ok` is True if success and False otherwise.
            When

        Raise:
            ValueError: input is invalid.
        """

        ## Maybe this can be changed to filtering options and output options instead? to be more generic.
        ## Although it will make everything more confusing if the user has to build the option dict himself
        output_resolution = output_resolution or self.output_resolution or 10
        output_crs = output_crs or self.output_crs or 4326

        aoi_param = Struct()
        aoi_param.update(aoi)

        if type(start_date) == str:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()

        if type(start_date) != datetime.date:
            raise ValueError("Invalid start_date, should be a datetime.date object or a str in isoformat")

        if type(end_date) == str:
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

        if type(end_date) != datetime.date:
            raise ValueError("Invalid end_date, should be a datetime.date object or a str in isoformat")

        if start_date == end_date:
            end_date = end_date + datetime.timedelta(days=1)
            logger.warning("start_date and end_date are the same, adding 1 day to end_date")

        filtering_options = Struct()
        filtering_options.update({"data_coverage": data_coverage})

        output_options = Struct()
        output_options.update(
            {
                "save_to_bucket": False,
                "save_to_file": False,
                "crs": output_crs,
                "resolution": output_resolution,
            }
        )

        # Allow to transfer up to 500mo as grpc message
        channel_opt = [
            ("grpc.max_send_message_length", config.GRPC_MAX_SEND_MESSAGE_LENGTH),
            ("grpc.max_receive_message_length", config.GRPC_MAX_RECEIVE_MESSAGE_LENGTH),
        ]
        # with grpc.insecure_channel(config.BACKEND_URL, options=channel_opt,) as channel:

        with grpc.secure_channel(
            self.backend_url,
            grpc.composite_channel_credentials(
                grpc.ssl_channel_credentials(config.CERT), grpc.metadata_call_credentials(GrpcAuth(self.api_key))
            ),
            options=channel_opt,
        ) as channel:
            stub = backend_pb2_grpc.BackendStub(channel)
            responses = stub.GetS1ARD(
                backend_pb2.GetS1ArdRequest(
                    id=self.id,
                    aoi=aoi_param,
                    start_date=start_date.isoformat(),
                    end_date=end_date.isoformat(),
                    filtering_options=filtering_options,
                    output_options=output_options,
                )
            )

            logger.info(f"Waiting for computation result, id={self.id} ...")

            items = []
            try:
                for response in responses:
                    logger.info(
                        f"Received result for date={response.date}, status={response.status}"
                        + (f", reason={response.reason}" if response.reason else "")
                    )
                    if response.status == "success":
                        if self.save_to_local:
                            output_dir = os.path.join(self.local_output_path, response.id)
                            file_path = os.path.join(output_dir, f"{response.date}.tiff")
                            os.makedirs(output_dir, exist_ok=True)
                            with open(file_path, "wb") as file:
                                file.write(response.data)
                            result = Sentinel1ResultItem(
                                response.date, response.status, response.data, file_path=file_path
                            )
                        else:
                            result = Sentinel1ResultItem(response.date, response.status)
                    else:
                        result = Sentinel1ResultItem(
                            response.date,
                            response.status,
                            file_path=None,
                            reason=response.reason,
                        )
                    items.append(result)
                return Sentinel1Result(items=items)
            except grpc.RpcError as e:
                logger.warning(e.details())
                return Sentinel1Result(ok=False, reason=e.details())

    def compute_s1_ard_from_search_result(
        self,
        search_result: Sentinel1SearchResult,
        output_resolution: int = None,
        output_crs: int = None,
    ) -> Sentinel1Result:

        output_resolution = output_resolution or self.output_resolution or 10
        output_crs = output_crs or self.output_crs or 4326

        aoi_param = Struct()
        aoi_param.update(search_result.aoi)

        filtering_options = Struct()
        filtering_options.update({"data_coverage": search_result.data_coverage})

        output_options = Struct()
        output_options.update(
            {
                "save_to_bucket": False,
                "save_to_file": False,
                "crs": output_crs,
                "resolution": output_resolution,
            }
        )

        # Allow to transfer up to 500mo as grpc message
        channel_opt = [
            ("grpc.max_send_message_length", config.GRPC_MAX_SEND_MESSAGE_LENGTH),
            ("grpc.max_receive_message_length", config.GRPC_MAX_RECEIVE_MESSAGE_LENGTH),
        ]
        # with grpc.insecure_channel(config.BACKEND_URL, options=channel_opt,) as channel:

        search_results_dict = {scene["title"]: scene for scene in search_result.to_dict}
        search_results_dict = make_scenes_serializable(search_results_dict)

        search_results_struct = Struct()
        search_results_struct.update(search_results_dict)
        with grpc.secure_channel(
            self.backend_url,
            grpc.composite_channel_credentials(
                grpc.ssl_channel_credentials(config.CERT), grpc.metadata_call_credentials(GrpcAuth(self.api_key))
            ),
            options=channel_opt,
        ) as channel:
            stub = backend_pb2_grpc.BackendStub(channel)
            responses = stub.GetS1ARD(
                backend_pb2.GetS1ArdRequest(
                    id=self.id,
                    aoi=aoi_param,
                    filtering_options=filtering_options,
                    from_search_results=search_results_struct,
                    output_options=output_options,
                )
            )

            s1_results = Sentinel1Result()
            try:
                for response in responses:
                    scene_list = create_scene_list_object(response.scenes)
                    logger.info(
                        f"Received result for date={response.date}, status={response.status}"
                        + (f", reason={response.reason}" if response.reason else "")
                    )
                    if response.status == "success":
                        if self.save_to_local:
                            output_dir = os.path.join(self.local_output_path, response.id)
                            file_path = os.path.join(output_dir, f"{response.date}.tiff")
                            os.makedirs(output_dir, exist_ok=True)
                            with open(file_path, "wb") as file:
                                file.write(response.data)
                            result = Sentinel1ResultItem(
                                response.date, response.status, scene_list, response.data, file_path=file_path
                            )
                        else:
                            result = Sentinel1ResultItem(response.date, response.status, scene_list)
                    else:
                        result = Sentinel1ResultItem(
                            response.date,
                            response.status,
                            scene_list,
                            file_path=None,
                            reason=response.reason,
                        )
                    s1_results._items.append(result)
                return s1_results
            except grpc.RpcError as e:
                logger.warning(e.details())
                return Sentinel1Result(ok=False, reason=e.details())

    def s2_search(self, aoi, start_date, end_date, query_filters=None) -> Sentinel2SearchResult:
        """
        Search for Sentinel-2 scenes in a given area of interest.

        :param aoi: A GeoJSON polygon
        :param start_date: Start date of the search
        :param end_date: End date of the search
        :param query_filters: Filters to apply to the search query
        :return: A list of scenes for each date

        The result of s2_search is a pandas dataframe listing the scenes for your aoi and dates. To refine this search,
        simply select the scenes provided in the dataframe using pandas to set as a new (or overwritten) search result variable. This new result can then
        be passed to the fuse fuction.

        If only one date is needed, the start_date and end_date can be equal.
        """

        aoi_param = Struct()
        aoi_param.update(aoi)

        if type(start_date) == str:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()

        if type(start_date) != datetime.date:
            raise ValueError("Invalid start_date, should be a datetime.date object or a str in isoformat")

        if type(end_date) == str:
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

        if type(end_date) != datetime.date:
            raise ValueError("Invalid end_date, should be a datetime.date object or a str in isoformat")

        if start_date == end_date:
            end_date = end_date + datetime.timedelta(days=1)
            logger.warning("start_date and end_date are the same, adding 1 day to end_date")

        filters_param = Struct()
        if query_filters is not None:
            filters_param.update(query_filters)

        with grpc.secure_channel(
            self.backend_url,
            grpc.composite_channel_credentials(
                grpc.ssl_channel_credentials(config.CERT), grpc.metadata_call_credentials(GrpcAuth(self.api_key))
            ),
        ) as channel:
            stub = backend_pb2_grpc.BackendStub(channel)
            try:
                response = stub.GetS2Search(
                    backend_pb2.GetS2SearchRequest(
                        id=self.id,
                        aoi=aoi_param,
                        start_date=start_date.isoformat(),
                        end_date=end_date.isoformat(),
                        filters=filters_param,
                    )
                )

                geojson = json_format.MessageToDict(response.scenes)
                item_list = [Item(feature) for feature in geojson["features"]]
                collection_list = [Collection(collection) for collection in geojson["collections"]]
                item_collection = ItemCollection(items=item_list, collections=collection_list)
                return Sentinel2SearchResult(aoi, item_collection=item_collection)
            except grpc.RpcError as e:
                logger.warning(e.details())
                return Sentinel2SearchResult(aoi, item_collection=None, ok=False, reason=e.details())

    def fuse_custom(
        self,
        to_fuse: List[Union[Raster, Vector]],
        custom_params: Dict,
        aoi: Any = None,
        output_resolution: int = None,
        output_crs: int = None,
    ) -> FuseResult:
        """

        This method fuses georeferenced raster files with Sentinel-1 ARD, Sentinel-2 ARD for the specified AOI following the custom_params stategy
        It is a temporary function that will be replaced by a more generic way.

        For example, to get the closest sentinel-2 data from 2 sentinel-1 specified info (slave and master):
        | custom_params = {
        |    "first_info" : {"s1_date" : "2020-12-26", "s1_relative_orbit_number" : 81},
        |    "last_info" : {"s1_date" : "2021-01-20", "s1_relative_orbit_number" : 8},
        |    "s1_data_coverage" : 100,
        |    "s2_data_coverage" : 100
        | }
        |
        | Custom params description :
        | s1_date (isoformat date): (required) sentinel-1 date
        | s1_relative_orbit_number (int): (optional) sentinel-1 relative orbit number
        | s1_data_coverage (int): (optional) minimum sentinel-1 result data coverage in percent, default is 100
        | s2_data_coverage (int): (optional) minimum sentinel-2 result data coverage in percent, default is 100

        Args:
            to_fuse (list): list containing Raster and/or Vector objects.
            custom_params (dict): params dictionary that describe the custom fuse behavior (see the example above)
            aoi (dict): Optional, geojson feature or feature collection dictionary containing a polygon. this argument will not be used if use_first_object_as_reference is set to True.

        Returns:
            :py:class:`FuseResult` :py:attr:`FuseResult.ok` is True if success and False otherwise.

        """
        output_resolution = output_resolution or self.output_resolution or None
        output_crs = output_crs or self.output_crs or None

        first_s1_date = custom_params["first_info"]["s1_date"]
        last_s1_date = custom_params["last_info"]["s1_date"]

        aoi_param = None
        if aoi:
            aoi_param = Struct()
            aoi_param.update(aoi)

        if type(first_s1_date) == str:
            first_s1_date = datetime.datetime.strptime(first_s1_date, "%Y-%m-%d").date()

        if type(first_s1_date) != datetime.date:
            raise ValueError(
                f"Invalid first_info.s1_date : {first_s1_date}, should be a datetime.date object or a str in isoformat"
            )

        if type(last_s1_date) == str:
            last_s1_date = datetime.datetime.strptime(last_s1_date, "%Y-%m-%d").date()

        if type(last_s1_date) != datetime.date:
            raise ValueError(
                f"Invalid last_info.s1_date : {last_s1_date}, should be a datetime.date object or a str in isoformat"
            )

        if first_s1_date == last_s1_date:
            logger.warning("first_info.s1_date and last_info.s1_date are the same")

        s1_data_coverage = custom_params["s1_data_coverage"] if "s1_data_coverage" in custom_params else None
        if s1_data_coverage is not None:
            if int(s1_data_coverage) > 100 or int(s1_data_coverage) < 0:
                raise ValueError(f"Invalid s1_data_coverage : {s1_data_coverage}, should be between 0 and 100")

        s2_data_coverage = custom_params["s2_data_coverage"] if "s2_data_coverage" in custom_params else None
        if s2_data_coverage is not None:
            if int(s2_data_coverage) > 100 or int(s2_data_coverage) < 0:
                raise ValueError(f"Invalid s2_data_coverage : {s2_data_coverage}, should be between 0 and 100")

        params = Struct()
        params.update(custom_params)

        output_options = Struct()
        output_options.update(
            {
                "crs": output_crs,
                "resolution": output_resolution,
            }
        )

        # Allow to transfer up to 500mo as grpc message
        channel_opt = [
            ("grpc.max_send_message_length", config.GRPC_MAX_SEND_MESSAGE_LENGTH),
            ("grpc.max_receive_message_length", config.GRPC_MAX_RECEIVE_MESSAGE_LENGTH),
        ]
        with grpc.secure_channel(
            self.backend_url,
            grpc.composite_channel_credentials(
                grpc.ssl_channel_credentials(config.CERT), grpc.metadata_call_credentials(GrpcAuth(self.api_key))
            ),
            options=channel_opt,
        ) as channel:
            stub = backend_pb2_grpc.BackendStub(channel)
            request = backend_pb2.FuseCustomRequest(
                id=self.id,
                aoi=aoi_param,
                params=params,
                output_options=output_options,
            )
            # load raster and vector files
            for file_iterator in to_fuse:
                file_iterator.add_to_request(request)

            try:
                response = stub.FuseCustom(request)
                if response.status != "success":
                    logger.info("failed")
                    return FuseResult(
                        ok=False,
                        reason=response.reason,
                        status=response.status,
                    )
                if not self.save_to_local:
                    return FuseResult(ok=True, reason=response.reason, status=response.status, data=response.data)
                output_dir = os.path.join(self.local_output_path, self.id)
                file_path = os.path.join(output_dir, f"{self.id}.nc")
                os.makedirs(output_dir, exist_ok=True)
                with open(file_path, "wb") as file:
                    file.write(response.data)
                logger.info("created everything")
                return FuseResult(
                    ok=True,
                    reason=response.reason,
                    status=response.status,
                    file_path=file_path,
                )
            except grpc.RpcError as e:
                logger.error(e.details())
                return FuseResult(
                    ok=False,
                    reason=e.details(),
                )

    def fuse(
        self,
        catalogs_list: List[Union[Sentinel1SearchResult, Sentinel2SearchResult]],
        fuse_id: str = None,
        aoi: Any = None,
        to_fuse: List[Union[Raster, Vector]] = [],
        additional_info: dict = None,
        output_resolution: int = None,
        output_crs: int = None,
    ) -> FuseResult:
        """Fuses Sentinel-1 ARD and Sentinel-2 ARD with any provided georeferenced raster and/or vector files over a specified area of interest (AOI).

        In order to change the behavior of this method you can use other methods of :py:class:`Client`.

        Please note, resampling is performed using a nearest resampling technique. For this alpha version, there is no way to change the resampling type. However, this feature is coming soon.

        Args:
            catalogs_list: List containing Sentinel1SearchResult and Sentinel2SearchResult objects,
            to_fuse (list): list containing Raster and/or Vector objects.
            aoi (dict): Optional, geojson feature or feature collection dictionary containing a polygon. this argument will not be used if use_first_object_as_reference is set to True.

        Returns:
            :py:class:`FuseResult` :py:attr:`FuseResult.ok` is True if success and False otherwise.

        Raise:
            ValueError: input is invalid.
        """
        output_resolution = output_resolution or self.output_resolution or None
        output_crs = output_crs or self.output_crs or None

        params = Struct()
        if additional_info is not None:
            params.update({"additional_info": additional_info})

        if not catalogs_list:
            raise ValueError("You need at least one Sentinel1SearchResult() or one Sentinel2SearchResult()")
        elif has_duplicates(catalogs_list):
            raise ValueError(
                f"Got multiple catalogs of the same type '{type(has_duplicates(catalogs_list))}'. expected a maximum of one for each catalog type"
            )
        elif has_empty_dataframe(catalogs_list):
            raise ValueError(f"{type(has_empty_dataframe(catalogs_list))}.dataframe is empty")

        catalogs_dict = {
            "s1": {"bands": [], "query_results": [], "sequence_index": 0},
            "s2": {"bands": [], "query_results": [], "sequence_index": 1},
        }
        for idx, catalog in enumerate(catalogs_list):
            if type(catalog) == Sentinel2SearchResult and catalog.ok:
                search_results_dict = make_geojson_serializable(catalog.to_dict)
                catalogs_dict["s2"]["bands"].extend(catalog.output_bands)
                catalogs_dict["s2"]["query_results"].append(search_results_dict)
                catalogs_dict["s2"]["sequence_index"] = idx
            elif type(catalog) == Sentinel1SearchResult and catalog.ok:
                catalogs_dict["s1"]["bands"].extend(catalog.output_bands)
                search_results_dict = {scene["title"]: scene for scene in catalog.to_dict}
                search_results_dict = make_scenes_serializable(search_results_dict)
                catalogs_dict["s1"]["query_results"].append(search_results_dict)
                catalogs_dict["s1"]["sequence_index"] = idx

        search_results_struct = Struct()
        search_results_struct.update(catalogs_dict)

        aoi_param = Struct()
        if aoi:
            aoi_param.update(aoi)
        else:
            aoi_param.update(catalogs_list[0].aoi)

        output_options = Struct()
        output_options.update(
            {
                "save_to_bucket": False,
                "save_to_file": False,
                "crs": output_crs,
                "resolution": output_resolution,
            }
        )

        # Allow to transfer up to 500mo as grpc message
        channel_opt = [
            ("grpc.max_send_message_length", config.GRPC_MAX_SEND_MESSAGE_LENGTH),
            ("grpc.max_receive_message_length", config.GRPC_MAX_RECEIVE_MESSAGE_LENGTH),
        ]
        with grpc.secure_channel(
            self.backend_url,
            grpc.composite_channel_credentials(
                grpc.ssl_channel_credentials(config.CERT), grpc.metadata_call_credentials(GrpcAuth(self.api_key))
            ),
            options=channel_opt,
        ) as channel:
            stub = backend_pb2_grpc.BackendStub(channel)
            request = backend_pb2.FuseRequest(
                id=self.id,
                aoi=aoi_param,
                params=params,
                output_options=output_options,
                search_results=search_results_struct,
            )
            # load raster and vector files
            for file_iterator in to_fuse:
                file_iterator.add_to_request(request)

            try:
                response = stub.Fuse(request)
                if response.status != "success":
                    logger.info("failed")
                    return FuseResult(
                        ok=False,
                        reason=response.reason,
                        status=response.status,
                    )
                output_dir = os.path.join(self.local_output_path, self.id)
                filename = fuse_id if fuse_id else self.id
                if not self.save_to_local:
                    return FuseResult(
                        ok=True,
                        reason=response.reason,
                        status=response.status,
                        data=response.data,
                        base_dir=self.local_output_path,
                        client_id=self.id,
                        fuse_id=fuse_id,
                    )

                file_path = os.path.join(output_dir, f"{filename}.nc")
                os.makedirs(output_dir, exist_ok=True)
                with open(file_path, "wb") as file:
                    file.write(response.data)
                result = FuseResult(
                    ok=True,
                    reason=response.reason,
                    status=response.status,
                    file_path=file_path,
                    base_dir=self.local_output_path,
                    client_id=self.id,
                    fuse_id=fuse_id,
                )
                logger.info("created everything")
                return result
            except grpc.RpcError as e:
                logger.error(e.details())
                return FuseResult(
                    ok=False,
                    reason=e.details(),
                )

    def fuse_from_search(
        self,
        catalogs_list: List[Union[Sentinel1SearchResult, Sentinel2SearchResult]],
        fuse_id: str = None,
        aoi: Any = None,
        to_fuse: List[Union[Raster, Vector]] = [],
        additional_info: dict = None,
        output_resolution: int = None,
        output_crs: int = None,
    ) -> FuseResult:
        """Deprecated, use fuse instead."""
        logger.warning("fuse_from_search is deprecated, use fuse instead")
        self.fuse(
            catalogs_list=catalogs_list,
            fuse_id=fuse_id,
            aoi=aoi,
            to_fuse=to_fuse,
            additional_info=additional_info,
            output_resolution=output_resolution,
            output_crs=output_crs,
        )

    @staticmethod
    def load_s1_ard_from_local(id: str, root_dir: str = "./generated"):
        """Load a previous S1 ARD computation result from local disk.

        Args:
            id (str): previously computed ARD id.
            root_dir(str): root directory where the ARD computation results are stored.

        Returns:
            :py:class:`Sentinel1Result`

        """

        items = []
        work_dir = os.path.join(root_dir, id)
        if not id:
            raise ValueError("id is required")
        if not os.path.isdir(work_dir):
            raise ValueError(f"Previous computation result with id {id} could not found ({work_dir})")
        for filename in os.listdir(work_dir):
            file_path = os.path.join(work_dir, filename)
            result = Sentinel1ResultItem(None, "success", file_path=file_path)
            items.append(result)
        return Sentinel1Result(items=items)


def make_scenes_serializable(d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make a dictionary serializable by ray.put
    """
    for key, value in d.items():
        for sub_key, sub_value in value.items():
            if isinstance(sub_value, datetime.datetime) or isinstance(sub_value, datetime.date):
                d[key][sub_key] = sub_value.isoformat()
    return d


def make_geojson_serializable(d: Union[dict, list]) -> Union[dict, list]:
    """
    Make a dictionary serializable for gRPC
    """
    if type(d) is dict:
        iterator_with_key = d.items()
    elif type(d) is list:
        iterator_with_key = enumerate(d)
    else:
        return d

    for key, value in iterator_with_key:
        if isinstance(value, datetime.date):
            d[key] = value.isoformat()
        elif type(value) is dict or type(value) is list:
            d[key] = make_geojson_serializable(value)
        else:
            continue
    return d


def create_scene_list_object(scene_list_message: Struct) -> list:
    """
    Create a Sentinel1SceneList object from a protobuf message
    """
    return list(json_format.MessageToDict(scene_list_message).values())


def has_duplicates(list: list):
    """Check if given list contains any duplicates"""
    compare_set = set()
    for elem in list:
        if elem in compare_set:
            return elem
        else:
            compare_set.add(elem)
    return None


def has_empty_dataframe(list: list):
    """Check if given list contains empty dataset"""
    for elem in list:
        if elem.dataframe.empty:
            return elem
    return None
