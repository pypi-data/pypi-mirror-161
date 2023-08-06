# Copyright 2022 Cognite AS

import os
from typing import Iterator, List, Optional

from cognite.seismic._api.api import API
from cognite.seismic._api.grpc_helpers import get_single_item, reraise_notfound
from cognite.seismic._api.utility import get_identifier
from cognite.seismic.data_classes.api_types import IngestionJob, SegyOverrides, SourceSegyFile, TraceHeaderField
from cognite.seismic.data_classes.searchspec import SearchSpecBase, SearchSpecFile

if not os.getenv("READ_THE_DOCS"):
    from cognite.seismic.protos.types_pb2 import CRS, ExternalId
    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import Dimensions
    from cognite.seismic.protos.v1.seismic_service_messages_pb2 import (
        EditSourceSegyFileRequest,
        IngestSourceSegyFileRequest,
        RegisterSourceSegyFileRequest,
        SearchFilesRequest,
        UnregisterSourceSegyFileRequest,
    )


class FileAPI(API):
    def __init__(self, seismic, ingestion):
        self.seismic = seismic
        super().__init__(ingestion=ingestion)

    @staticmethod
    def _verify_input(crs: str = None, wkt: str = None, geo_json: str = None):
        if not crs:
            raise Exception("CRS is required")
        if not wkt and not geo_json:
            raise Exception("Either `wkt` or `geo_json` needs to be specified")
        if wkt and geo_json:
            raise Exception("Only `wkt` or `geo_json` should be specified")

    def list(self) -> Iterator[SourceSegyFile]:
        """List all files.

        Returns:
            Iterator[:py:class:`~cognite.seismic.data_classes.api_types.SourceSegyFile`]: A stream of Files.
        """
        request = SearchFilesRequest()
        return (SourceSegyFile._from_proto(f) for f in self.seismic.SearchFiles(request))

    def search(self, *, search_spec: SearchSpecBase) -> Iterator[SourceSegyFile]:
        """Search for files.

        Args:
            search_spec (:py:class:`~cognite.seismic.data_classes.searchspec.SearchSpecBase`):
                One of :py:class:`~cognite.seismic.SearchSpecSurvey`,
                :py:class:`~cognite.seismic.SearchSpecFile`,
                :py:class:`~cognite.seismic.SearchSpecSeismicStore`, or
                :py:class:`~cognite.seismic.SearchSpecGetAll`.
                Specifies the search parameters.

        Returns:
            Iterator[:py:class:`~cognite.seismic.data_classes.api_types.SourceSegyFile`]: A stream of found Files.
        """
        req = search_spec._to_search_files_request()

        return reraise_notfound(SourceSegyFile._from_proto(f) for f in self.seismic.SearchFiles(req))

    def get(
        self, *, id: Optional[int] = None, uuid: Optional[str] = None, external_id: Optional[str] = None
    ) -> SourceSegyFile:
        """Fetch a file by id.

        Args:
            id (int, optional): The id of the file to fetch
            uuid (str, optional): The id of the file to fetch in the old uuid format
            external_id (str, optional): The external id of the file to fetch

        Returns:
            :py:class:`~cognite.seismic.data_classes.api_types.SourceSegyFile`: The retrieved file
        """

        spec_count = sum([id is not None, external_id is not None, uuid is not None])
        if spec_count == 1:
            result = self.search(search_spec=SearchSpecFile(id=id, external_id=external_id, uuid=uuid))
            return get_single_item(result, "File not found.")
        elif spec_count > 1:
            raise ValueError("Only one of id, external_id and uuid can be specified.")
        elif spec_count == 0:
            raise ValueError("id, external_id or uuid must be specified.")

    def register(
        self,
        *,
        survey_id: Optional[int] = None,
        survey_external_id: Optional[str] = None,
        path: str,
        external_id: str,
        metadata: dict = None,
        crs: Optional[str] = None,
        energy_source_point_offset: Optional[int] = None,
        cdp_number_offset: Optional[int] = None,
        inline_offset: Optional[int] = None,
        crossline_offset: Optional[int] = None,
        cdp_x_offset: Optional[int] = None,
        cdp_y_offset: Optional[int] = None,
        shotpoint_offset: Optional[int] = None,
        source_group_scalar_override: Optional[float] = None,
        dimensions: int = 3,
        key_fields: List[TraceHeaderField] = [],
    ) -> SourceSegyFile:
        """Register a source SEG-Y file for ingestion.

        Args:
            survey_id (int, optional):
                The id of the survey this source file belongs to.
                The survey is identified by either the id or the external id. If both are provided, the id is used.
            survey_external_id (str, optional):
                The external id of the survey this source file belongs to.
                The survey is identified by either the id or the external id. If both are provided, the id is used.
            path (str):
                Cloud storage path including protocol, bucket, directory structure, and file name.
                Example: "gs://cognite-seismic-eu/samples/DN1302M03R16_MERGED_KPSDM_00-32_DEG_T.sgy".
            external_id (str): External id to assign to the file
            metadata (dict, optional): A string -> string dictionary with any metadata to add about the file
            crs (str, optional):
                The CRS of the file as an EPSG code (e.g. "EPSG:4326").
                If not given, the CRS will be taken from the survey.
            energy_source_point_offset (int, optional):
                Position of the energy source point in trace headers.
                Defaults to 17 as per the SEG-Y rev1 specification.
            cdp_number_offset (int, optional):
                Position of the ensemble (CDP) number in trace headers.
                Defaults to 21 as per the SEG-Y rev1 specification.
            inline_offset (int, optional):
                Position of the inline number field in the trace headers.
                Defaults to 189 as per the SEG-Y rev1 specification.
            crossline_offset (int, optional):
                Position of the crossline number field in the trace headers.
                Defaults to 193 as per the SEG-Y rev1 specification.
            cdp_x_offset (int, optional):
                Position of the X coordinate of ensemble (CDP) in trace headers.
                Defaults to 181 as per the SEG-Y rev1 specification.
            cdp_y_offset (int, optional):
                Position of the Y coordinate of ensemble (CDP) in trace headers.
                Defaults to 185 as per the SEG-Y rev1 specification.
            shotpoint_offset (int, optional):
                Position of the shotpoint field in trace headers.
                Defaults to 197 as per the SEG-Y rev1 specification.
            source_group_scalar_override:
                Multiplier for CDP-X and CDP-Y values, overrides scalar factor
                obtained from trace header. Note that this is a straight
                multiplier to be applied, not a value to be interpreted like
                the SEG-Y trace header field. Valid values for this parameter
                are in the range 0.0 < n <= 1.0
            dimensions (int, optional): File data dimensionality, either 2 or 3. Defaults to 3.
            key_fields (List[:py:class:`~cognite.seismic.TraceHeaderField`], optional):
                The trace header fields that will be used as keys for indexing.
                Defaults to [INLINE, CROSSLINE] for 3D files, and [CDP] for 2D.

        Returns:
            :py:class:`~cognite.seismic.data_classes.api_types.SourceSegyFile`: The registered source file
        """
        if dimensions == 2:
            dimensions_enum = Dimensions.Value("TWO_DEE")
        elif dimensions == 3:
            dimensions_enum = Dimensions.Value("THREE_DEE")
        else:
            raise Exception("Invalid `dimensions`. Must be either 2 or 3")

        crs = CRS(crs=crs) if crs is not None else None

        key_fields_enum = list(map(lambda f: f._to_proto(), key_fields))

        segy_overrides = SegyOverrides(
            energy_source_point_offset=energy_source_point_offset,
            cdp_number_offset=cdp_number_offset,
            inline_offset=inline_offset,
            crossline_offset=crossline_offset,
            cdp_x_offset=cdp_x_offset,
            cdp_y_offset=cdp_y_offset,
            shotpoint_offset=shotpoint_offset,
            source_group_scalar_override=source_group_scalar_override,
        )

        request = RegisterSourceSegyFileRequest(
            survey=get_identifier(survey_id, survey_external_id),
            path=path,
            external_id=ExternalId(external_id=external_id),
            metadata=metadata,
            crs=crs,
            segy_overrides=segy_overrides._to_proto(),
            key_fields=key_fields_enum,
            dimensions=dimensions_enum,
        )
        return SourceSegyFile._from_proto(self.seismic.RegisterSourceSegyFile(request).file)

    def edit(
        self,
        *,
        id: Optional[int] = None,
        external_id: Optional[str] = None,
        path: Optional[str] = None,
        new_external_id: Optional[str] = None,
        metadata: dict = None,
        crs: Optional[str] = None,
        energy_source_point_offset: Optional[int] = None,
        cdp_number_offset: Optional[int] = None,
        inline_offset: Optional[int] = None,
        crossline_offset: Optional[int] = None,
        cdp_x_offset: Optional[int] = None,
        cdp_y_offset: Optional[int] = None,
        shotpoint_offset: Optional[int] = None,
        source_group_scalar_override: Optional[float] = None,
        dimensions: Optional[int] = None,
        key_fields: List[TraceHeaderField] = [],
    ) -> SourceSegyFile:
        """Edit a previously registered source SEG-Y file.

        Pass a value of 0 to any override argument to remove that override.

        Args:
            id (int, optional): The id of the source file to edit.
            external_id (str, optional): The external id of the source file to edit.
            path (str, optional):
                Cloud storage path including protocol, bucket, directory structure, and file name.
                Example: "gs://cognite-seismic-eu/samples/DN1302M03R16_MERGED_KPSDM_00-32_DEG_T.sgy".
            new_external_id (str, optional): An external identifier - matches service contract field.
            metadata (Dict[str, str], optional): Any custom-defined metadata.
            crs (str, optional): Official name of the CRS used. Example: "EPSG:23031".
            energy_source_point_offset (int, optional): Position of the energy source point in trace headers.
            cdp_number_offset (int, optional): Position of the ensemble (CDP) number in trace headers.
            inline_offset (int, optional): Position of the inline number field in the trace headers.
            crossline_offset (int, optional): Position of the crossline number field in the trace headers.
            cdp_x_offset (int, optional): Position of the X coordinate of ensemble (CDP) in trace headers.
            cdp_y_offset (int, optional): Position of the Y coordinate of ensemble (CDP) in trace headers.
            shotpoint_offset (int, optional): Position of the shotpoint field in trace headers.
            source_group_scalar_override (float, optional): Position of the energy source point in trace headers.
            dimensions (int, optional): File data dimensionality, either 2 or 3.
            key_fields (List[:py:class:`~cognite.seismic.TraceHeaderField`], optional):
                The trace header fields that will be used as keys for indexing.

        Returns:
            :py:class:`~cognite.seismic.SourceSegyFile`: The registered source file
        """

        if dimensions is None:
            dimensions_enum = None
        elif dimensions == 2:
            dimensions_enum = Dimensions.Value("TWO_DEE")
        elif dimensions == 3:
            dimensions_enum = Dimensions.Value("THREE_DEE")
        else:
            raise Exception("Invalid `dimensions`. Must be either 2 or 3")

        key_fields_enum = list(map(lambda f: f._to_proto(), key_fields))

        segy_overrides = SegyOverrides(
            energy_source_point_offset=energy_source_point_offset,
            cdp_number_offset=cdp_number_offset,
            inline_offset=inline_offset,
            crossline_offset=crossline_offset,
            cdp_x_offset=cdp_x_offset,
            cdp_y_offset=cdp_y_offset,
            shotpoint_offset=shotpoint_offset,
            source_group_scalar_override=source_group_scalar_override,
        )

        request = EditSourceSegyFileRequest(
            file=get_identifier(id, external_id),
            path=path,
            external_id=None if new_external_id is None else ExternalId(external_id=new_external_id),
            metadata=metadata,
            crs=None if crs is None else CRS(crs=crs),
            segy_overrides=segy_overrides._to_proto(),
            key_fields=key_fields_enum,
            dimensions=dimensions_enum,
        )
        return SourceSegyFile._from_proto(self.seismic.EditSourceSegyFile(request).file)

    def unregister(self, *, id: Optional[int] = None, external_id: Optional[str] = None):
        """Unregister a previously registered source SEG-Y file. If the file
        has been ingested or queued for ingestion, the seismicstore must first
        be deleted.

        Args:
            id (int, optional): The id of the source file to unregister.
            external_id (str, optional): The external id of the source file to unregister.
        """

        request = UnregisterSourceSegyFileRequest(file=get_identifier(id, external_id))
        self.seismic.UnregisterSourceSegyFile(request)

    def ingest(
        self,
        *,
        file_id: Optional[int] = None,
        file_external_id: Optional[str] = None,
        storage_tier: Optional[str] = None,
    ) -> IngestionJob:
        """Ingest a registered file.

        Args:
            file_id (int, optional): File id of the registered source file to ingest.
            file_external_id (str, optional): External id of the registered source file to ingest.
            storage_tier (str, optional):
                Target storage tier. A storage tier is a defined facility for storing the trace data
                associated with a seismic volume.

        Returns:
            :py:class:`~cognite.seismic.data_classes.api_types.IngestionJob`:
                A job id that can be used to query for status of the ingestion job.
        """
        request = IngestSourceSegyFileRequest(
            file=get_identifier(file_id, file_external_id), target_storage_tier_name=storage_tier
        )
        return IngestionJob._from_proto(self.seismic.IngestSourceSegyFile(request))
