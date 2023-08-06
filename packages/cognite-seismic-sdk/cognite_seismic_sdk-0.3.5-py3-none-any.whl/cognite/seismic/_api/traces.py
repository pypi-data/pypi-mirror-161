# Copyright 2022 Cognite AS

import os
import sys
from typing import Iterator, Optional

import numpy as np
from cognite.seismic._api.api import API
from cognite.seismic._api.utility import LineRange, get_identifier
from cognite.seismic.data_classes.api_types import (
    ArrayData,
    ArrayData2d,
    ArrayData3d,
    Trace,
    TraceBounds,
    TraceBounds2d,
    TraceBounds3d,
    TraceHeaderField,
)
from cognite.seismic.data_classes.extents import RangeInclusive, SeismicExtent
from cognite.seismic.data_classes.geometry import Geometry, InterpolationMethod

if not os.getenv("READ_THE_DOCS"):
    from cognite.seismic.protos.types_pb2 import LineDescriptor
    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import GeometryFilter
    from cognite.seismic.protos.v1.seismic_service_messages_pb2 import SegYSeismicRequest, StreamTracesRequest
    from google.protobuf.wrappers_pb2 import Int32Value as i32
else:
    from cognite.seismic._api.shims import LineDescriptor


class TracesAPI(API):
    def __init__(self, query, ingestion):
        super().__init__(query=query, ingestion=ingestion)
        try:
            from tqdm.auto import tqdm

            self.tqdm = tqdm
        except ImportError:
            self.tqdm = None
        self.is_interactive = hasattr(sys, "ps1")
        self.has_warned = False

    @staticmethod
    def _build_trace_request(
        seismic_id: Optional[int] = None,
        seismic_external_id: Optional[str] = None,
        seismic_store_id: Optional[int] = None,
        extent: Optional[SeismicExtent] = None,
        geometry: Optional[Geometry] = None,
        interpolation_method: Optional[InterpolationMethod] = None,
        z_range: Optional[LineRange] = None,
        include_trace_header: bool = False,
    ):

        have_seismic_id = seismic_id is not None or seismic_external_id is not None
        if seismic_store_id is not None and have_seismic_id:
            raise ValueError("Provide either seismic_store_id or a seismic identifier, not both")

        if seismic_store_id is None and not have_seismic_id:
            raise ValueError("Provide either seismic_store_id or a seismic identifier")

        if geometry is not None and extent is not None:
            raise ValueError(
                "Got both a geometry filter and an extent object. Provide a \
                geometry filter or an extent, but not both."
            )
        if geometry is None and interpolation_method is not None:
            raise ValueError(
                "Got an interpolation method argument, but no geometry filter. \
                Interpolation is only supported on certain geometry filters and \
                data, and a geometry filter must be provided."
            )

        z_range = into_line_descriptor(z_range)

        req = StreamTracesRequest(include_trace_header=include_trace_header, z_range=z_range)

        if seismic_store_id is not None:
            req.seismic_store_id = seismic_store_id
        else:
            req.seismic.MergeFrom(get_identifier(seismic_id, seismic_external_id))

        if extent is not None:
            extent._merge_into_stream_traces_request(req)

        if geometry is not None:
            interpolation_method = interpolation_method.value if interpolation_method is not None else 0
            flt = GeometryFilter(geometry=geometry._to_proto(), interpolation_method=interpolation_method)
            req.geometry.MergeFrom(flt)

        return req

    @staticmethod
    def _build_seg_y_request(
        seismic_id: Optional[int] = None,
        seismic_external_id: Optional[str] = None,
        seismic_store_id: Optional[int] = None,
        extent: Optional[SeismicExtent] = None,
        geometry: Optional[Geometry] = None,
    ):

        have_seismic_id = seismic_id is not None or seismic_external_id is not None
        if seismic_store_id is not None and have_seismic_id:
            raise ValueError("Provide either seismic_store_id or a seismic identifier, not both")

        if seismic_store_id is None and not have_seismic_id:
            raise ValueError("Provide either seismic_store_id or a seismic identifier")

        if geometry is not None and extent is not None:
            raise ValueError(
                "Got both a geometry filter and an extent object. Provide a geometry filter or an extent, but not both."
            )

        req = SegYSeismicRequest()

        if seismic_store_id is not None:
            req.seismic_store_id = seismic_store_id
        else:
            req.seismic.MergeFrom(get_identifier(seismic_id, seismic_external_id))

        if extent is not None:
            extent._merge_into_segy_seismic_request(req)

        if geometry is not None:
            req.polygon.MergeFrom(geometry._to_proto())

        return req

    def stream_traces(self, **kwargs) -> Iterator[Trace]:
        """Retrieve traces from a seismic or seismic store

        Provide one of: the seismic id, the seismic external id, the seismic store id.

        Traces can be filtered by a geometry, by line ranges, or by a SeismicExtent object for
        more advanced line-based filtering. The line ranges are specified as tuples of either
        (start, end) or (start, end, step). If a filter is not specified, the maximum ranges
        will be assumed.

        Note that while both inline_range and xline_range may be specified at the same time,
        only one of cdp_range, shotpoint_range or energy_source_point_range may be specified.

        Args:
            seismic_id (int, optional): The id of the seismic to query
            seismic_external_id (str, optional): The external id of the seismic to query
            seismic_store_id (int, optional): The id of the seismic store to query
            extent (:py:class:`~cognite.seismic.SeismicExtent`, optional):
                A SeismicExtent object indicating which traces to include
            geometry (:py:class:`~cognite.seismic.Geometry`, optional):
                Return traces inside this geometry (if area-like) or interpolate traces onto a line
                (if line-like; only valid for 3d objects).
            interpolation_method (:py:class:`~cognite.seismic.InterpolationMethod`, optional):
                Interpolation method to use when interpolating traces. Only valid if `geometry`
                is a line-like geometry.
            z_range (line range, optional): The range of depth indices to include.
                Specified as a tuple of (int, int) or (int, int, int),
                representing start index, end index, and step size respectively.
            include_trace_header (bool, optional): Whether to include trace header info in the response.

        Returns:
            Iterator[:py:class:`~cognite.seismic.data_classes.api_types.Trace`], the traces for the specified volume
        """

        req = self._build_trace_request(**kwargs)
        for proto in self.query.StreamTraces(req):
            yield Trace._from_proto(proto)

    def get_segy(self, **kwargs) -> Iterator[bytes]:
        """Retrieve traces in binary format from a seismic or seismic store

        Provide one of: the seismic id, the seismic external id, the seismic store id.

        The first and second elements in the response stream will always be the text header
        and binary header of the file.

        Traces can be filtered by a geometry, by line ranges, or by a SeismicExtent object for
        more advanced line-based filtering. The line ranges are specified as tuples of either
        (start, end) or (start, end, step). If a filter is not specified, the maximum ranges
        will be assumed.

        Note that while both inline_range and xline_range may be specified at the same time,
        only one of cdp_range, shotpoint_range or energy_source_point_range may be specified.

        Args:
            seismic_id (int, optional): The id of the seismic to query
            seismic_external_id (str, optional): The external id of the seismic to query
            seismic_store_id (int, optional): The id of the seismic store to query
            extent (:py:class:`~cognite.seismic.SeismicExtent`, optional):
                A SeismicExtent object indicating which traces to include
            geometry (:py:class:`~cognite.seismic.Geometry`, optional):
                Return traces inside this geometry (if area-like) or interpolate traces onto a line
                (if line-like; only valid for 3d objects).

        Returns:
            An Iterator of bytes buffers that, when concatenated, constitute a SEG-Y stream.
        """

        req = self._build_seg_y_request(**kwargs)
        for proto in self.query.GetSegYFile(req):
            yield proto.content

    def get_trace_bounds(self, **kwargs) -> TraceBounds:
        """Compute the amount of data that will be returned for a given stream_traces request.
        This may be used to allocate sufficient data in an array, and also describes the range of the key
        header fields used to identify traces, ie. the range of the inline and xline numbers for 3D data, or
        the CDP or shotpoint field values for 2D data.

        Parameters: See :py:meth:`~TracesAPI.stream_traces`

        Returns:
            A :py:class:`~TraceBounds` object describing the size and bounds of the returned traces
        """
        req = self._build_trace_request(**kwargs)
        bounds_proto = self.query.GetTraceBounds(req)

        return TraceBounds._from_proto(bounds_proto)

    # Refuse to allocate arrays larger than this
    # FIXME(audunska): Figure out the right limit here, or maybe just use numpy's memory limit
    ARR_LIM = 1e8

    def get_array(self, *, progress: Optional[bool] = None, **kwargs) -> ArrayData:
        """Store traces from a seismic or seismic store into a numpy array

        Parameters: See :py:meth:`~TracesAPI.stream_traces`.

        In addition, there's an optional boolean argument :code:`progress`, which
        turns a progress bar on or off and defaults to :code:`True`.

        Returns:
            An :py:class:`~ArrayData` object encapsulating the retrieved array (see below)
        """

        req = self._build_trace_request(**kwargs)
        bounds_proto = self.query.GetTraceBounds(req)
        bounds = TraceBounds._from_proto(bounds_proto)

        two_dee = isinstance(bounds, TraceBounds2d)
        three_dee = isinstance(bounds, TraceBounds3d)

        if not (two_dee or three_dee):
            # This means the bounds is the base class TraceBounds, which happens if
            # the geometry was line-like
            raise ValueError("get_array not supported for line-like geometries")

        if three_dee:
            return self._get_array_3d(req, bounds, progress)
        elif two_dee:
            return self._get_array_2d(req, bounds, bounds_proto.two_dee_bounds.cdp_bounds, progress)

    def _add_progress(self, req, num_traces, progress: Optional[bool] = None):
        if progress is None:
            progress = self.is_interactive
        if progress and self.tqdm is None and not self.has_warned:
            print("Warning: Progress bar requires the tqdm library, which is not installed.", file=sys.stderr)
            print("Disabling progress bar. Install with 'pip install tqdm'.", file=sys.stderr)
            self.has_warned = True
        if self.tqdm is None:
            progress = False
        stream = self.query.StreamTraces(req)
        if progress:
            return self.tqdm(stream, total=num_traces)
        else:
            return stream

    def _get_array_3d(self, req, bounds: TraceBounds3d, progress: Optional[bool] = None) -> ArrayData3d:
        z_size = len(bounds.z_range)

        # Bail out early if empty
        if bounds.inline_bounds is None or bounds.xline_bounds is None:
            trace_data = np.ma.masked_all((0, 0, z_size), dtype="float")
            coord_x = np.ma.masked_all((0, 0), dtype="float")
            coord_y = np.ma.masked_all((0, 0), dtype="float")
            return ArrayData3d(
                trace_data=trace_data,
                coord_x=coord_x,
                coord_y=coord_y,
                crs=bounds.crs,
                inline_range=None,
                xline_range=None,
                z_range=bounds.z_range,
            )

        inline_size = len(bounds.inline_bounds)
        xline_size = len(bounds.xline_bounds)

        if inline_size * xline_size * z_size > self.ARR_LIM:
            raise ValueError(
                f"Array of size ({inline_size},{xline_size},{z_size}) has more \
                than the maximum {self.ARR_LIM} elements. Consider restricting \
                the returned volume using stricter trace filters."
            )

        trace_data = np.ma.masked_all((inline_size, xline_size, z_size), dtype="float")
        coord_x = np.ma.masked_all((inline_size, xline_size), dtype="float")
        coord_y = np.ma.masked_all((inline_size, xline_size), dtype="float")

        # Fetch data
        for trace in self._add_progress(req, bounds.num_traces, progress):
            inline_ind = bounds.inline_bounds.index(trace.iline.value)
            xline_ind = bounds.xline_bounds.index(trace.xline.value)
            trace_data[inline_ind, xline_ind, :] = trace.trace
            coord_x[inline_ind, xline_ind] = trace.coordinate.x
            coord_y[inline_ind, xline_ind] = trace.coordinate.y
        return ArrayData3d(
            trace_data=trace_data,
            crs=bounds.crs,
            coord_x=coord_x,
            coord_y=coord_y,
            inline_range=bounds.inline_bounds,
            xline_range=bounds.xline_bounds,
            z_range=bounds.z_range,
        )

    def _get_array_2d(
        self, req, bounds: TraceBounds2d, cdp_bounds: Optional[LineRange], progress: Optional[bool] = None
    ) -> ArrayData2d:
        z_size = len(bounds.z_range)

        # Bail out early if empty
        if bounds.trace_key_bounds is None or cdp_bounds is None:
            trace_data = np.ma.masked_all((0, z_size), dtype="float")
            coord_x = np.ma.masked_all((0,), dtype="float")
            coord_y = np.ma.masked_all((0,), dtype="float")
            return ArrayData2d(
                trace_data=trace_data,
                coord_x=coord_x,
                coord_y=coord_y,
                crs=bounds.crs,
                trace_key_header=bounds.trace_key_header,
                trace_key_values=np.ma.masked_all((0,), dtype="int"),
                z_range=bounds.z_range,
            )

        cdp_bounds = RangeInclusive._from_proto(cdp_bounds)
        cdp_size = len(cdp_bounds)

        if cdp_size * z_size > self.ARR_LIM:
            raise ValueError(
                f"Array of size ({cdp_size},{z_size}) has more than the \
                maximum of {self.ARR_LIM} elements. Consider restricting the \
                returned volume using stricter trace filters."
            )

        trace_data = np.ma.masked_all((cdp_size, z_size), dtype="float")
        coord_x = np.ma.masked_all((cdp_size,), dtype="float")
        coord_y = np.ma.masked_all((cdp_size,), dtype="float")
        trace_key_values = np.ma.masked_all((cdp_size,), dtype="int")

        if bounds.trace_key_header == TraceHeaderField.CDP:
            trace_key_field = "cdp"
        elif bounds.trace_key_header == TraceHeaderField.SHOTPOINT:
            trace_key_field = "shotpoint"
        elif bounds.trace_key_header == TraceHeaderField.ENERGY_SOURCE_POINT:
            trace_key_field = "energy_source_point"
        else:
            # This case should have been caught by the GetTraceBounds call,
            # but bail out here anyway, just in case
            raise ValueError(f"Invalid 2d trace key header {bounds.trace_key_header}.")

        # Fetch data
        for trace in self._add_progress(req, bounds.num_traces, progress):
            # This case should also have been caught by the GetTraceBounds call
            if not trace.HasField(trace_key_field):
                raise ValueError(f"Trace does not have a value for {bounds.trace_key_header}")
            key = getattr(trace, trace_key_field).value

            if not trace.HasField("cdp"):
                raise ValueError("Trace does not have a value for CDP")
            cdp = trace.cdp.value
            ind = cdp_bounds.index(cdp)

            trace_data[ind, :] = trace.trace
            coord_x[ind] = trace.coordinate.x
            coord_y[ind] = trace.coordinate.y
            trace_key_values[ind] = key
        return ArrayData2d(
            trace_data=trace_data,
            coord_x=coord_x,
            coord_y=coord_y,
            crs=bounds.crs,
            trace_key_header=bounds.trace_key_header,
            trace_key_values=trace_key_values,
            z_range=bounds.z_range,
        )


def into_line_descriptor(linerange: Optional[LineRange]) -> Optional[LineDescriptor]:
    "Converts a tuple of two or three values into a LineDescriptor"
    if linerange is None:
        return None
    if len(linerange) == 2:
        start, stop = linerange
        return LineDescriptor(min=i32(value=start), max=i32(value=stop))
    if len(linerange) == 3:
        start, stop, step = linerange
        return LineDescriptor(min=i32(value=start), max=i32(value=stop), step=i32(value=step))
    raise Exception("A line range should be None, (int, int), or (int, int, int).")
