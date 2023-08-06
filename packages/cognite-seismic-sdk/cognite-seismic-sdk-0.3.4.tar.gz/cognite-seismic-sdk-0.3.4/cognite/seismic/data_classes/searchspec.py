import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from cognite.seismic._api.utility import get_search_spec

if not os.getenv("READ_THE_DOCS"):
    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import SearchSpec
    from cognite.seismic.protos.v1.seismic_service_messages_pb2 import (
        SearchFilesRequest,
        SearchSeismicsRequest,
        SearchSeismicStoresRequest,
    )
else:
    from cognite.seismic._api.shims import (
        SearchFilesRequest,
        SearchSeismicsRequest,
        SearchSeismicStoresRequest,
        SearchSpec,
    )


def _get_search_spec_from_base(base: "SearchSpecBase") -> SearchSpec:
    return get_search_spec(
        base.id, base.external_id, base.external_id_substring, base.name, base.name_substring, base.uuid
    )


@dataclass
class SearchSpecBase(ABC):
    """Base class for search specs. The concrete implementations are
    :py:class:`~cognite.seismic.data_classes.searchspec.SearchSpecGetAll`,
    :py:class:`~cognite.seismic.data_classes.searchspec.SearchSpecSurvey`,
    :py:class:`~cognite.seismic.data_classes.searchspec.SearchSpecSeismicStore`,
    :py:class:`~cognite.seismic.data_classes.searchspec.SearchSpecFile`.
    """

    id: Optional[int] = None
    external_id: Optional[str] = None
    external_id_substring: Optional[str] = None
    name: Optional[str] = None
    name_substring: Optional[str] = None
    uuid: Optional[str] = None

    @abstractmethod
    def _to_search_seismicstores_request(self) -> SearchSeismicStoresRequest:
        pass

    @abstractmethod
    def _to_search_seismics_request(self) -> SearchSeismicsRequest:
        pass

    @abstractmethod
    def _to_search_files_request(self) -> SearchFilesRequest:
        pass


class SearchSpecGetAll:
    """Defines a spec to search for all objects."""

    def _to_search_seismicstores_request(self) -> SearchSeismicStoresRequest:
        """Create a SearchSeismicStoreRequst that will fetch all seismic stores"""
        return SearchSeismicStoresRequest()

    def _to_search_seismics_request(self) -> SearchSeismicsRequest:
        return SearchSeismicsRequest()

    def _to_search_files_request(self) -> SearchFilesRequest:
        return SearchFilesRequest()


class SearchSpecSurvey(SearchSpecBase):
    """Defines a spec to search for objects by survey identifiers."""

    def _to_search_seismicstores_request(self) -> SearchSeismicStoresRequest:
        """Convert this search spec into a SearchSeismicStoreRequest."""
        return SearchSeismicStoresRequest(survey=_get_search_spec_from_base(self))

    def _to_search_seismics_request(self) -> SearchSeismicsRequest:
        return SearchSeismicsRequest(survey=_get_search_spec_from_base(self))

    def _to_search_files_request(self) -> SearchFilesRequest:
        return SearchFilesRequest(survey=_get_search_spec_from_base(self))


class SearchSpecSeismicStore(SearchSpecBase):
    """Defines a spec to search for seismic stores by seismic store identifiers."""

    def _to_search_seismicstores_request(self) -> SearchSeismicStoresRequest:
        """Convert this search spec into a SearchSeismicStoreRequest."""
        return SearchSeismicStoresRequest(seismic_store=_get_search_spec_from_base(self))

    def _to_search_seismics_request(self) -> SearchSeismicsRequest:
        raise TypeError("Cannot search for seismics by seismic store")

    def _to_search_files_request(self) -> SearchFilesRequest:
        return SearchFilesRequest(seismic_store=_get_search_spec_from_base(self))


class SearchSpecFile(SearchSpecBase):
    """Defines a spec to search for seismic stores by file identifiers."""

    uuid: Optional[str] = None

    def _to_search_seismicstores_request(self) -> SearchSeismicStoresRequest:
        """Convert this search spec into a SearchSeismicStoreRequest."""
        return SearchSeismicStoresRequest(file=_get_search_spec_from_base(self))

    def _to_search_seismics_request(self) -> SearchSeismicsRequest:
        raise TypeError("Cannot search for seismics by file")

    def _to_search_files_request(self) -> SearchFilesRequest:
        return SearchFilesRequest(spec=_get_search_spec_from_base(self))


class SearchSpecPartition(SearchSpecBase):
    """Defines a spec to search for seismics by partition."""

    def _to_search_seismicstores_request(self) -> SearchSeismicStoresRequest:
        raise TypeError("Cannot search for seismic stores by partition")

    def _to_search_seismics_request(self) -> SearchSeismicsRequest:
        """Converts search spec into SearchSeismicsRequest"""
        return SearchSeismicsRequest(partition=_get_search_spec_from_base(self))

    def _to_search_files_request(self) -> SearchFilesRequest:
        raise TypeError("Cannot search for files by partition")


class SearchSpecSeismic(SearchSpecBase):
    """Defines a spec to search for seismics by seismic identifiers."""

    def _to_search_seismicstores_request(self) -> SearchSeismicStoresRequest:
        raise TypeError("Cannot search for seismic stores by seismic")

    def _to_search_seismics_request(self) -> SearchSeismicsRequest:
        """Converts search spec into SearchSeismicsRequest"""
        return SearchSeismicsRequest(seismic=_get_search_spec_from_base(self))

    def _to_search_files_request(self) -> SearchFilesRequest:
        raise TypeError("Cannot search for files by seismic")
