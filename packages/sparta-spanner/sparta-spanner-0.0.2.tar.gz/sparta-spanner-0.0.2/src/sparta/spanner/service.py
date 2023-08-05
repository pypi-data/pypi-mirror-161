import _queue
import logging
from typing import TypeVar, Callable

from google.api_core import exceptions
from google.cloud import spanner
from google.cloud.spanner_v1.database import Database
from google.cloud.spanner_v1.snapshot import Snapshot
from google.cloud.spanner_v1.transaction import Transaction

from sparta.spanner.concurrency import run_as_non_blocking

_T = TypeVar("_T")


class DBService:
    def __init__(
        self,
        project_id,
        instance_id,
        database_id,
        pool_size=None,
        session_request_timeout=None,
    ):
        """
        :param project_id: Google Cloud project ID (e.g. 'spartaproduct')
        :param instance_id: Spanner instance ID
        :param database_id: Spanner database ID
        """
        if not project_id:
            raise ValueError("Missing project_id")
        if not instance_id:
            raise ValueError("Missing instance_id")
        if not database_id:
            raise ValueError("Missing database_id")

        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Create session pool
        _pool = None
        if pool_size:
            _pool = spanner.FixedSizePool(
                size=pool_size, default_timeout=session_request_timeout
            )

        # Create client
        self._spanner_client = spanner.Client()
        self._instance = self._spanner_client.instance(instance_id)
        self._database = self._instance.database(database_id, pool=_pool)

        self._logger.info(
            f"Created {type(self).__name__} for {project_id}/{instance_id}/{database_id}"
        )

    def ping(self):
        self.execute_sql("SELECT 1")

    def execute_sql(self, *arg, **kwarg):
        with self._database.snapshot() as s:
            return s.execute_sql(*arg, **kwarg)

    async def run_in_snapshot(
        self,
        snapshot_consumer: Callable[[Snapshot], _T],
        *args,
        **kwargs,
    ) -> _T:
        def task():
            try:
                with self._database.snapshot(*args, **kwargs) as snapshot:
                    return snapshot_consumer(snapshot)
            except _queue.Empty as error:
                raise NoSessionAvailableException() from error  # exception chaining

        return await run_as_non_blocking(task)

    async def run_in_transaction(
        self,
        transaction_consumer: Callable[[Transaction], _T],
        *args,
        **kwargs,
    ) -> _T:
        def task():
            try:
                return self._database.run_in_transaction(
                    transaction_consumer, *args, **kwargs
                )
            except _queue.Empty as error:
                raise NoSessionAvailableException() from error  # exception chaining
            except exceptions.Aborted as error:
                raise TimeoutError() from error  # exception chaining

        return await run_as_non_blocking(task)


class NoSessionAvailableException(Exception):
    pass
