from itertools import count
from typing import Any, Generic, Tuple, TypeVar, cast
import asyncio
import logging

from sarus_data_spec.constants import CACHE, CACHE_PATH
from sarus_data_spec.context import global_context
from sarus_data_spec.status import (
    error,
    last_status,
    last_statuses,
    processing,
    ready,
)
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st


class DataSpecErrorStatus(Exception):
    ...


T = TypeVar("T")

logger = logging.getLogger(__name__)


class StatusAwareComputation(Generic[T]):
    """Singleton visitor class template to perform basic status checks.

    This class' purpose if to manage statuses, before, during and after a
    DataSpec's computation. It also manages caching.

    This class is intended to be subclassed and used in a Manager's
    `async_to_XXX` method. For instance, to implement `Manager.async_to_arrow`
    the idea is to implement a subclass ArrowComputation(Iterator[pa.
    RecordBatch]) and to do ArrowComputation.accept(dataspec).

    Subclasses must only implement the __read_from_cache__, __write_to_cache__
    and __process__ methods.
    """

    @classmethod
    async def accept(
        cls, dataspec: st.DataSpec, *args: Any, **kwargs: Any
    ) -> T:
        """Apply the appropriate method depending on the status."""

        # this is to fix current different status behavior between DOD
        # and DATASPEC
        hot_fix_status(dataspec)

        statuses = last_statuses(dataspec, task=CACHE)
        # a dataspec is always cached in one place, so we can take
        # the first status for that for now

        if len(statuses) == 0:
            return await cls.process(dataspec, *args, **kwargs)
        else:
            cache_task = cast(st.Stage, statuses[0].task(CACHE))
            if cache_task.ready():
                # TODO: cls.ready should take a stage rather than
                # the status
                return await cls.ready(dataspec, statuses[0])
            elif cache_task.pending():
                return await cls.pending(dataspec, *args, **kwargs)
            elif cache_task.processing():
                return await cls.processing(
                    dataspec, *args, interval=20, attempts=10, **kwargs
                )
            elif cache_task.error():
                return await cls.error(dataspec, *args, **kwargs)
            else:
                raise ValueError(f"Inconsistent status {statuses[0]}")

    @classmethod
    async def processing(
        cls,
        dataspec: st.DataSpec,
        *args: Any,
        attempts: int = 10,
        interval: int = 20,
        **kwargs: Any,
    ) -> T:
        """If processing, wait for the dataspec to be ready.

        Such a case can happen if another manager has launched the computation
        of this DataSpec's value. A timeout period is defined after which the
        computation is relaunched (this is a default behavior intended to be
        improved in the future).

        Args:
            attempts (int): number of attempts before timing out.
            interval (int): number of seconds between attempts.
        """
        attempt = count()
        while next(attempt) <= attempts:
            # TODO: in principle, here only one manager can be
            # processing the operation but have to be sure
            status = last_status(dataspec, task=CACHE)
            assert status
            if not status.processing():
                break
            await asyncio.sleep(interval)

        status = last_status(dataspec)
        assert status
        if status.processing():
            # Still processing, process anyway
            # TODO might not be a good idea to relaunch
            # a really long computation
            return await cls.process(dataspec, *args, **kwargs)
        else:
            # computation finished, revisit to define what to do
            return await cls.accept(dataspec, *args, **kwargs)

    @classmethod
    async def error(
        cls,
        dataspec: st.DataSpec,
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """The DataSpec already has an Error status.
        In this case we clear the error and relaunch
        the process"""
        # we want to erase all the statuses of the
        # dataspec concerning the CACHE
        statuses = dataspec.storage().referring(
            dataspec, type_name=sp.type_name(sp.Status)
        )
        for status in statuses:
            status = cast(st.Status, status)
            if status.task(CACHE) is not None:
                dataspec.storage().delete(status.uuid())
        return await cls.accept(dataspec, *args, **kwargs)

    @classmethod
    async def pending(
        cls, dataspec: st.DataSpec, *args: Any, **kwargs: Any
    ) -> T:
        """The DataSpec has been added to the computation queue.

        No manager has undertaken the computation yet."""
        return await cls.process(dataspec, *args, **kwargs)

    @classmethod
    async def process(
        cls, dataspec: st.DataSpec, *args: Any, **kwargs: Any
    ) -> T:
        """Compute the DataSpec's value.

        Set the DataSpec's status to PROCESSING and launch the computation
        defined in the subclass.

        If an error occurs, set the status to ERROR with the Exception
        representation.

        If no error occurs, write the result to cache, set the status to READY
        with the cache path and return the actual value.
        """
        manager = global_context().manager()
        processing(
            dataspec=dataspec,
            manager=manager,
            task=CACHE,
        )
        try:
            result = await cls.__process__(dataspec, *args, **kwargs)
        except Exception as e:
            error(
                dataspec=dataspec,
                manager=manager,
                task=CACHE,
                properties={"message": repr(e)},
            )
            logger.exception(e)
            raise DataSpecErrorStatus(repr(e))
        else:
            cache_path, result = await cls.__write_to_cache__(dataspec, result)
            ready(
                dataspec=dataspec,
                manager=manager,
                task=CACHE,
                properties={CACHE_PATH: cache_path},
            )
            return result

    @classmethod
    def cache_path(cls, status: st.Status) -> str:
        task_cache = status.task(CACHE)
        assert task_cache is not None
        assert task_cache.ready()
        path = task_cache.properties()[CACHE_PATH]
        if path:
            return path
        raise ValueError('Cache was not found')

    @classmethod
    async def ready(cls, dataspec: st.DataSpec, status: st.Status) -> T:
        """Read the value from the cache."""
        return await cls.__read_from_cache__(dataspec, status)

    @classmethod
    async def __read_from_cache__(
        cls, dataspec: st.DataSpec, status: st.Status
    ) -> T:
        # Should be implemented for each to_XXX method
        raise NotImplementedError

    @classmethod
    async def __write_to_cache__(
        cls, dataspec: st.DataSpec, data: T
    ) -> Tuple[str, T]:
        # Should be implemented for each to_XXX method
        raise NotImplementedError

    @classmethod
    async def __process__(
        cls,
        dataspec: st.DataSpec,
        *args: Any,
        **kwargs: Any,
    ) -> T:
        # Must be reimplemented for each to_XXX method
        raise NotImplementedError


def hot_fix_status(dataspec: st.DataSpec) -> None:
    """Currently, in DOD, status tasks are given
    by the protobuf name, so we create a status for
    the cache task manually
    """
    statuses = last_statuses(dataspec)
    for status in statuses:
        for task_name in status.protobuf().task_stages.keys():
            path = status.task(task_name).properties()["cache"]  # type:ignore
            if path:
                logging.warn(
                    f'Cache was found in task {task_name},'
                    f' but it should be in {CACHE}, added by hot_fix'
                )
                ready(dataspec, task=CACHE, properties={CACHE_PATH: path})
