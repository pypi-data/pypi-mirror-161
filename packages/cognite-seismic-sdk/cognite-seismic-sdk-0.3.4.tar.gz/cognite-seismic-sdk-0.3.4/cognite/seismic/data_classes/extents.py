import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, Iterator, List, Mapping, Optional, Tuple, Union

from cognite.seismic._api.utility import Direction, LineRange
from cognite.seismic.data_classes.geometry import Geometry

if not os.getenv("READ_THE_DOCS"):
    from cognite.seismic.protos.types_pb2 import LineDescriptor
    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import MinorLines
    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import Seismic2dExtent as Seismic2dExtentProto
    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import Seismic3dDef as Seismic3dDefProto
    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import Seismic3dExtent as Seismic3dExtentProto
    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import Seismic3dRect as Seismic3dRectProto
    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import Seismic3dRects as Seismic3dRectsProto
    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import SeismicCutout as SeismicCutoutProto
    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import SeismicExtent as SeismicExtentProto
    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import TraceHeaderField as TraceHeaderFieldProto
    from cognite.seismic.protos.v1.seismic_service_messages_pb2 import (
        CreateSeismicRequest,
        SegYSeismicRequest,
        StreamTracesRequest,
    )
    from google.protobuf.wrappers_pb2 import Int32Value as i32
else:
    from cognite.seismic._api.shims import (
        CreateSeismicRequest,
        LineDescriptor,
        SegYSeismicRequest,
        Seismic2dExtentProto,
        Seismic3dDefProto,
        Seismic3dExtentProto,
        Seismic3dRectProto,
        Seismic3dRectsProto,
        SeismicCutoutProto,
        SeismicExtentProto,
        StreamTracesRequest,
    )


class TraceHeaderField(Enum):
    """Used to reference a key trace header field."""

    INLINE = 3
    "Inline number in a 3D grid"
    CROSSLINE = 4
    "Crossline number in a 3d grid"

    CDP = 2
    "Common depth point number"
    ENERGY_SOURCE_POINT = 1
    """Energy source point number. Usually means the same as shotpoint, but has
    a different standard location according to the SEGY spec."""
    SHOTPOINT = 5
    """Shotpoint number. Usually means the same as energy source point, but has
    a different standard location according to the SEGY spec."""

    @staticmethod
    def _from_proto(proto) -> "TraceHeaderField":
        if proto is None or proto < 1 or proto > 5:
            raise ValueError(f"Unrecognized TraceHeaderField: {proto}")
        return TraceHeaderField(proto)

    def _to_proto(self):
        return TraceHeaderFieldProto.values()[self.value]

    # The default repr gives the enum value, which is a bit more detail than needed for end users.
    # The str value is a bit nicer.
    def __repr__(self):
        return str(self)


class RangeInclusive:
    """Represents an inclusive range of inlines/xlines or depth coordinates.

    Attributes:
        start: The first linenumber encompassed by the range
        stop: The last linenumber encompassed by the range
        step: The distance between linenumbers"""

    start: int
    stop: int
    step: int

    def __init__(self, start: int, stop: int, step: Optional[int] = None):
        if step == 0:
            raise ValueError("RangeInclusive(): step must be nonzero")
        if step is None:
            step = 1 if stop >= start else -1
        self.start = start
        self.stop = start + ((stop - start) // step) * step
        self.step = step

    @staticmethod
    def _from_proto(proto: LineDescriptor) -> "RangeInclusive":
        start = proto.min.value
        if start is None:
            raise ValueError("LineDescriptor: start is None")
        stop = proto.max.value
        if stop is None:
            raise ValueError("LineDescriptor: stop is None")
        step = proto.step.value if proto.step is not None and proto.step.value != 0 else 1
        return RangeInclusive(start, stop, step)

    @staticmethod
    def from_linerange(linerange: LineRange) -> "RangeInclusive":
        """Construct a RangeInclusive from a (start, stop) or (start, stop, step) tuple"""
        if len(linerange) == 2:
            if linerange[0] < linerange[1]:
                step = 1
            else:
                step = -1
            return RangeInclusive(linerange[0], linerange[1], step)
        elif len(linerange) == 3:
            return RangeInclusive(linerange[0], linerange[1], linerange[2])
        else:
            raise ValueError("LineRange must have 2 or 3 elements")

    @staticmethod
    def _from_inds(inds: Iterable[int]) -> List["RangeInclusive"]:
        """Builds an optimal list of ranges from a list of indices"""

        def pop_range(first: int, sorted_rest: Iterator[int]) -> Tuple["RangeInclusive", Optional[int]]:
            step = 1
            prev = None
            for cur in sorted_rest:
                if prev is None:
                    step = cur - first
                    prev = cur
                else:
                    if prev + step == cur:
                        prev = cur
                    else:
                        return RangeInclusive(first, prev, step), cur
            if prev is None:
                return RangeInclusive(first, first), None
            else:
                return RangeInclusive(first, cur, step), None

        inds = iter(sorted(inds))
        ranges = []
        first = None
        try:
            first = next(inds)
        except StopIteration:
            pass
        while first is not None:
            r, first = pop_range(first, inds)
            ranges.append(r)

        return ranges

    def _to_proto(self) -> LineDescriptor:
        this = self.to_positive()
        step = None if this.step == 1 else i32(value=this.step)
        return LineDescriptor(min=i32(value=this.start), max=i32(value=this.stop), step=step)

    @staticmethod
    def _widest(ranges: Iterable[Tuple[int, int]]) -> "RangeInclusive":
        """Finds the widest range among the (min, max) tuples in ranges, and returns the result as a RangeInclusive"""
        min_start = None
        max_stop = None
        for (start, stop) in ranges:
            if min_start is None or start < min_start:
                min_start = start
            if max_stop is None or stop > max_stop:
                max_stop = stop
        if min_start is None or max_stop is None:
            raise ValueError("Empty range")
        return RangeInclusive(min_start, max_stop)

    def index(self, line: int) -> int:
        """Compute the index of a given linenumber in this range"""
        out_of_range = ValueError(f"line {line} out of range")
        incompatible = ValueError(f"line {line} incompatible with step {self.step} starting from {self.start}")
        if self.step > 0:
            if line < self.start or line > self.stop:
                raise out_of_range
            if (line - self.start) % self.step != 0:
                raise incompatible
            return (line - self.start) // self.step
        else:
            if line > self.start or line < self.stop:
                raise out_of_range
            if (line - self.start) % self.step != 0:
                raise incompatible
            return (self.start - line) // (-self.step)

    def to_linerange(self) -> LineRange:
        """Return a (start, stop) or a (start, stop, step) tuple"""
        if self.step == 1:
            return (self.start, self.stop)
        else:
            return (self.start, self.stop, self.step)

    def to_positive(self) -> "RangeInclusive":
        """Return an equivalent RangeInclusive where the step size is always positive"""
        if self.step > 0:
            return self
        else:
            return RangeInclusive(self.stop, self.start, -self.step)

    def __len__(self) -> int:
        """Return the number of lines described by this range"""
        return (self.stop - self.start) // self.step + 1

    def __iter__(self):
        cur = self.start
        while (self.step > 0 and cur <= self.stop) or (self.step < 0 and cur >= self.stop):
            yield cur
            cur += self.step

    def __contains__(self, line: int) -> bool:
        return line >= self.start and line <= self.stop and (line - self.start) % self.step == 0

    def __repr__(self):
        return f"RangeInclusive({self.start}, {self.stop}, {self.step})"

    def __eq__(self, other):
        same_start_stop = self.start == other.start and self.stop == other.stop
        if self.start == self.stop:
            # Singleton ranges, so it doesn't matter what the steps are
            return same_start_stop
        else:
            return same_start_stop and self.step == other.step


class SeismicCutout(ABC):
    """
    Describes how a Seismic object is cut out of the containing
    SeismicStore. This is an abstract class: Concrete instances will be one of the following:

    * A subclass of :py:class:`SeismicExtent` for describing exactly which traces to include
    * A geometry wrapped in a :py:class:`GeometryCutout` object
    * :py:class:`EmptyCutout` to explicitly describe an empty seismic object
    * :py:class:`FullCutout` to describe a seismic containing all the data in the seismic store
    """

    @abstractmethod
    def _to_cutout_proto(self) -> SeismicCutoutProto:
        pass

    @abstractmethod
    def _merge_into_create_seismic_request(self, request: CreateSeismicRequest):
        pass

    @staticmethod
    def _from_proto(proto: SeismicCutoutProto) -> "SeismicCutout":
        if proto.HasField("two_dee_extent"):
            return Seismic2dExtent._from_proto(proto.two_dee_extent)
        elif proto.HasField("three_dee_extent"):
            return Seismic3dExtent._from_proto(proto.three_dee_extent)
        elif proto.HasField("geometry"):
            return GeometryCutout(geometry=Geometry._from_proto(proto.geometry))
        elif proto.empty:
            return EmptyCutout()
        elif proto.full:
            return FullCutout()
        else:
            raise Exception("Invalid SeismicCutout protobuf")


class SeismicExtent(SeismicCutout):
    """Describes a selection of traces in a seismic object. This is an abstract
    class: Concrete instances will be either :py:class:`Seismic2dExtent` or a
    subclass of :py:class:`Seismic3dExtent`"""

    @staticmethod
    def _from_proto(proto: SeismicExtentProto) -> "SeismicExtent":
        if proto.HasField("two_dee_extent"):
            return Seismic2dExtent._from_proto(proto.two_dee_extent)
        elif proto.HasField("three_dee_extent"):
            return Seismic3dExtent._from_proto(proto.three_dee_extent)
        else:
            raise Exception("Invalid SeismicExtent protobuf")

    @abstractmethod
    def _to_extent_proto(self) -> SeismicExtentProto:
        pass

    @abstractmethod
    def dimensions(self) -> int:
        pass

    @abstractmethod
    def _merge_into_stream_traces_request(self, request: StreamTracesRequest):
        pass

    @abstractmethod
    def _merge_into_segy_seismic_request(self, request: SegYSeismicRequest):
        pass


@dataclass
class EmptyCutout(SeismicCutout):
    """Describes an empty cutout"""

    def _to_cutout_proto(self) -> SeismicCutoutProto:
        return SeismicCutoutProto(empty=True)

    def _merge_into_create_seismic_request(self, request: CreateSeismicRequest):
        request.empty = True


@dataclass
class FullCutout(SeismicCutout):
    """Describes a cutout filling its entire containing seismic store"""

    def _to_cutout_proto(self) -> SeismicCutoutProto:
        return SeismicCutoutProto(full=True)

    def _merge_into_create_seismic_request(self, request: CreateSeismicRequest):
        # Leave the volume oneof as null
        pass


@dataclass
class GeometryCutout(SeismicCutout):
    """Describes a cutout by a geometry.

    Attributes:
        geometry(:py:class:`~cognite.seismic.Geometry`): The geometry to cut by
    """

    geometry: Geometry

    def _to_cutout_proto(self) -> SeismicCutoutProto:
        return SeismicCutoutProto(geometry=self.geometry._to_proto())

    def _merge_into_create_seismic_request(self, request: CreateSeismicRequest):
        request.geometry.MergeFrom(self.geometry._to_proto())


@dataclass
class Seismic2dExtent(SeismicExtent):
    """Describes a selection of traces in a 2d seismic object.

    Attributes:
        trace_key (:py:class:`TraceHeaderField`): Which trace header field to select traces by
        ranges (List[:py:class:`RangeInclusive`]): A list of ranges of trace header values to include
    """

    trace_key: TraceHeaderField
    ranges: List[RangeInclusive]

    @staticmethod
    def from_lineranges(trace_key: TraceHeaderField, ranges: Iterable[LineRange]) -> "Seismic2dExtent":
        return Seismic2dExtent(trace_key, [RangeInclusive.from_linerange(r) for r in ranges])

    @staticmethod
    def cdp_ranges(ranges: Iterable[LineRange]) -> "Seismic2dExtent":
        """Create an extent filtering by a union of cdp ranges"""
        return Seismic2dExtent.from_lineranges(TraceHeaderField.CDP, ranges)

    @staticmethod
    def cdp_range(range: LineRange) -> "Seismic2dExtent":
        """Create an extent filtering by a single cdp range"""
        return Seismic2dExtent.cdp_ranges([range])

    @staticmethod
    def shotpoint_ranges(ranges: Iterable[LineRange]) -> "Seismic2dExtent":
        """Create an extent filtering by a union of shotpoint ranges"""
        return Seismic2dExtent.from_lineranges(TraceHeaderField.SHOTPOINT, ranges)

    @staticmethod
    def shotpoint_range(range: LineRange) -> "Seismic2dExtent":
        """Create an extent filtering by a single shotpoint range"""
        return Seismic2dExtent.shotpoint_ranges([range])

    @staticmethod
    def energy_source_point_ranges(ranges: Iterable[LineRange]) -> "Seismic2dExtent":
        """Create an extent filtering by a union of energy source point ranges"""
        return Seismic2dExtent.from_lineranges(TraceHeaderField.ENERGY_SOURCE_POINT, ranges)

    @staticmethod
    def energy_source_point_range(range: LineRange) -> "Seismic2dExtent":
        """Create an extent filtering by a single energy source point range"""
        return Seismic2dExtent.energy_source_point_ranges([range])

    @staticmethod
    def _from_proto(proto: Seismic2dExtentProto) -> "Seismic2dExtent":
        trace_key = TraceHeaderField._from_proto(proto.trace_key)
        ranges = [RangeInclusive._from_proto(ld) for ld in proto.trace_ranges]
        return Seismic2dExtent(trace_key=trace_key, ranges=ranges)

    def _to_2d_extent_proto(self) -> Seismic2dExtentProto:
        trace_ranges = [r._to_proto() for r in self.ranges]
        return Seismic2dExtentProto(trace_key=self.trace_key._to_proto(), trace_ranges=trace_ranges)

    def _to_extent_proto(self) -> SeismicExtentProto:
        return SeismicExtentProto(two_dee_extent=self._to_2d_extent_proto())

    def _to_cutout_proto(self) -> SeismicCutoutProto:
        return SeismicCutoutProto(two_dee_extent=self._to_2d_extent_proto())

    def _merge_into_create_seismic_request(self, request: CreateSeismicRequest):
        request.two_dee_extent.MergeFrom(self._to_2d_extent_proto())

    def _merge_into_stream_traces_request(self, request: StreamTracesRequest):
        request.two_dee_extent.MergeFrom(self._to_2d_extent_proto())

    def _merge_into_segy_seismic_request(self, request: SegYSeismicRequest):
        request.two_dee_extent.MergeFrom(self._to_2d_extent_proto())

    def dimensions(self) -> int:
        return 2


class Seismic3dExtent(SeismicExtent):
    """Describes a selection of traces in a 3d seismic object. This is an abstract
    class: Concrete instances will be either :py:class:`Seismic3dRect`,
    :py:class:`Seismic3dRects`, or :py:class:`Seismic3dDef`"""

    @staticmethod
    def _from_proto(proto: Seismic3dExtentProto) -> "Seismic3dExtent":
        if proto.HasField("rects"):
            if len(proto.rects.rects) == 1:
                return Seismic3dRect._from_proto(proto.rects.rects[0])
            else:
                return Seismic3dRects._from_proto(proto.rects)
        elif proto.HasField("def"):
            return Seismic3dDef._from_proto(getattr(proto, "def"))
        else:
            raise Exception("Invalid Seimsic3dExtent proto")

    @abstractmethod
    def _to_3d_extent_proto(self) -> Seismic3dExtentProto:
        pass

    def _to_extent_proto(self) -> SeismicExtentProto:
        return SeismicExtentProto(three_dee_extent=self._to_3d_extent_proto())

    def _to_cutout_proto(self) -> SeismicCutoutProto:
        return SeismicCutoutProto(three_dee_extent=self._to_3d_extent_proto())

    def _merge_into_create_seismic_request(self, request: CreateSeismicRequest):
        request.three_dee_extent.MergeFrom(self._to_3d_extent_proto())

    def _merge_into_stream_traces_request(self, request: StreamTracesRequest):
        request.three_dee_extent.MergeFrom(self._to_3d_extent_proto())

    def _merge_into_segy_seismic_request(self, request: SegYSeismicRequest):
        request.three_dee_extent.MergeFrom(self._to_3d_extent_proto())

    def dimensions(self) -> int:
        return 3


@dataclass
class Seismic3dRect(Seismic3dExtent):
    """Describes a selection of traces in a 3d seismic object as a stepped rectangle.

    To construct a :code:`Seismic3dRect`, pass either a :py:class`RangeInclusive` for the
    :code:`inline` and :code:`xline` arguments, or a tuple describing the start, and, and
    optionally step.

    A pair :code:`(il, xl)` is considered to be part of this extent if
    :code:`il` is part of the range :code:`inline` and :code:`xl` is part of the range
    :code:`xline`.

    Attributes:
        inline (:py:class:`RangeInclusive`): The range of inline values to include
        xline (:py:class:`RangeInclusive`): The range of xline values to include
    """

    inline: RangeInclusive
    xline: RangeInclusive

    def __init__(self, inline: Union[RangeInclusive, LineRange], xline: Union[RangeInclusive, LineRange]):
        if not isinstance(inline, RangeInclusive):
            inline = RangeInclusive.from_linerange(inline)
        if not isinstance(xline, RangeInclusive):
            xline = RangeInclusive.from_linerange(xline)
        self.inline = inline
        self.xline = xline

    @staticmethod
    def _from_proto(proto: Seismic3dRectProto) -> "Seismic3dRect":
        inline = RangeInclusive._from_proto(proto.inline_range)
        xline = RangeInclusive._from_proto(proto.xline_range)
        return Seismic3dRect(inline=inline, xline=xline)

    def _to_proto(self) -> Seismic3dRectProto:
        return Seismic3dRectProto(inline_range=self.inline._to_proto(), xline_range=self.xline._to_proto())

    def _to_3d_extent_proto(self) -> Seismic3dExtentProto:
        return Seismic3dRects([self])._to_3d_extent_proto()


@dataclass
class Seismic3dRects(Seismic3dExtent):
    """Describes a selection of traces in a 3d seismic object as a union of stepped rectangles.

    A pair :code:`(il, xl)` is considered to be part of this extent if it is part of at least one
    of the rectangles in :code:`rects`.

    Attributes:
        rects (List[:py:class:`Seismic3dRect`]): The list of rectangles in the union
    """

    rects: List[Seismic3dRect]

    @staticmethod
    def _from_proto(proto: Seismic3dRectsProto) -> "Seismic3dRects":
        return Seismic3dRects(rects=[Seismic3dRect._from_proto(r) for r in proto.rects])

    def _to_proto(self) -> Seismic3dRectsProto:
        return Seismic3dRectsProto(rects=[r._to_proto() for r in self.rects])

    def _to_3d_extent_proto(self) -> Seismic3dExtentProto:
        return Seismic3dExtentProto(rects=self._to_proto())


@dataclass
class Seismic3dDef(Seismic3dExtent):
    """
    Describes a selection of traces in a 3d seismic object as a mapping. For
    each major line (inline or xline) to include, provide a list of minor line
    ranges (xline or inline, respectively) to include for that major line.

    If :code:`major_header == Inline` and :code:`minor_header == Crossline`, a pair
    :code:`(il, xl)` is considered to be part of this extent if
    :code:`lines[il]` is populated and :code:`xl` is part of at least one of
    the ranges in :code:`lines[il]`. The situation with the opposite major / minor
    header is similar.

    Attributes:
        major_header (:py:class:`TraceHeaderField`): Either Inline or Crossline
        minor_header (:py:class:`TraceHeaderField`): Either Crossline or Inline, and different from major_header
        lines (Dict[int, List[:py:class:`RangeInclusive`]]): The mapping from major lines to minor ranges
    """

    major_header: TraceHeaderField
    minor_header: TraceHeaderField
    lines: Dict[int, List[RangeInclusive]]

    @staticmethod
    def _from_proto(proto: Seismic3dDefProto) -> "Seismic3dDef":
        major_header = TraceHeaderField._from_proto(proto.major_header)
        minor_header = TraceHeaderField._from_proto(proto.minor_header)
        lines: Dict[int, List[RangeInclusive]] = {}
        for major, minor_lines in proto.lines.items():
            lines[major] = [RangeInclusive._from_proto(ld) for ld in minor_lines.ranges]

        return Seismic3dDef(major_header=major_header, minor_header=minor_header, lines=lines)

    def _to_proto(self) -> Seismic3dDefProto:
        lines = {major: MinorLines(ranges=[r._to_proto() for r in ranges]) for major, ranges in self.lines.items()}
        return Seismic3dDefProto(
            major_header=self.major_header._to_proto(), minor_header=self.minor_header._to_proto(), lines=lines
        )

    def _to_3d_extent_proto(self) -> Seismic3dExtentProto:
        ext = Seismic3dExtentProto()
        getattr(ext, "def").MergeFrom(self._to_proto())
        return ext

    @staticmethod
    def inline_major(lines: Mapping[int, List[LineRange]]) -> "Seismic3dDef":
        """Create a Seismic3dDef mapping inlines to xline ranges

        Args:
            lines (Mapping[int, List[LineRange]]):
                A mapping from inline numbers to xline ranges in the
                (start, stop) or (start, stop, step) format.

        Returns:
            A :py:class:`Seismic3dDef` extent.
        """
        return Seismic3dDef.from_lineranges(Direction.INLINE, lines)

    @staticmethod
    def xline_major(lines: Mapping[int, List[LineRange]]) -> "Seismic3dDef":
        """Create a Seismic3dDef mapping xlines to inline ranges

        Args:
            lines (Mapping[int, List[LineRange]]):
                A mapping from xline numbers to inline ranges in the
                (start, stop) or (start, stop, step) format.

        Returns:
            A :py:class:`Seismic3dDef` extent.
        """
        return Seismic3dDef.from_lineranges(Direction.XLINE, lines)

    @staticmethod
    def from_lineranges(major_dir: Direction, lines: Mapping[int, List[LineRange]]) -> "Seismic3dDef":
        if major_dir == Direction.INLINE:
            major_header = TraceHeaderField.INLINE
            minor_header = TraceHeaderField.CROSSLINE
        elif major_dir == Direction.XLINE:
            major_header = TraceHeaderField.CROSSLINE
            minor_header = TraceHeaderField.INLINE
        lines = {major: [RangeInclusive.from_linerange(r) for r in ranges] for major, ranges in lines.items()}
        return Seismic3dDef(major_header=major_header, minor_header=minor_header, lines=lines)
