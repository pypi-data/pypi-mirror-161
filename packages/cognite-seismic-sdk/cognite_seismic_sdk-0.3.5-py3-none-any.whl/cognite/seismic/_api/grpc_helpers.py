from typing import Iterator, TypeVar

from cognite.seismic.data_classes.errors import NotFoundError
from grpc import RpcError, StatusCode

T = TypeVar("T")


# These methods are outside of utility.py to prevent circular import of NotFoundError


def get_single_item(iterator: Iterator[T], not_found_str: str) -> T:
    try:
        ret = next(iterator)
    except StopIteration:
        raise NotFoundError(not_found_str)
    try:
        next(iterator)
        raise Exception("Internal error: Found too many results. Please contact support.")
    except StopIteration:
        pass
    return ret


def reraise_notfound(iterator: Iterator[T]) -> Iterator[T]:
    """Wrap an iterator returned from a search endpoint to reraise NotFound as NotFoundError"""
    try:
        for element in iterator:
            yield element
    except RpcError as e:
        if e.code() == StatusCode.NOT_FOUND:
            raise NotFoundError(status=e.code(), message=e.details())
        else:
            raise e
