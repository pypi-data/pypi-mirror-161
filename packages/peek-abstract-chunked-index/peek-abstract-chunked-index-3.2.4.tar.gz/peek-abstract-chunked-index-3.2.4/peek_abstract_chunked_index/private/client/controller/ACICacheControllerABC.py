import json
import logging
from abc import ABCMeta
from datetime import datetime
from typing import Any
from typing import Callable
from typing import Dict
from typing import List

import pytz
from twisted.internet.defer import DeferredList
from twisted.internet.defer import inlineCallbacks
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope

from peek_abstract_chunked_index.private.tuples.ACIEncodedChunkTupleABC import (
    ACIEncodedChunkTupleABC,
)

ChunkedIndexChunkLoadRpcMethodType = Callable[
    [int, int], List[ACIEncodedChunkTupleABC]
]


class ACICacheControllerABC(metaclass=ABCMeta):
    """Chunked Index Cache Controller

    The Chunked Index cache controller stores all the chunks in memory,
    allowing fast access from the mobile and desktop devices.

    """

    _LOAD_CHUNK_SIZE = 24
    _LOAD_CHUNK_PARALLELISM = 6

    _ChunkedTuple: ACIEncodedChunkTupleABC = None
    _chunkLoadRpcMethod: ChunkedIndexChunkLoadRpcMethodType = None
    _updateFromServerFilt: Dict = None
    _logger: logging.Logger = None

    def __init__(self, clientId: str):
        assert self._ChunkedTuple, "_ChunkedTuple is None"
        assert self._chunkLoadRpcMethod, "_chunkLoadRpcMethod is None"
        assert self._updateFromServerFilt, "_updateFromServerFilt is None"
        assert self._logger, "_logger is None"

        self._clientId = clientId
        self._webAppHandler = None

        #: This stores the cache of chunkedIndex data for the clients
        self._cache: Dict[int, ACIEncodedChunkTupleABC] = {}

        self._endpoint = PayloadEndpoint(
            self._updateFromServerFilt, self._processChunkedIndexPayload
        )

    def setCacheHandler(self, handler):
        self._webAppHandler = handler

    @inlineCallbacks
    def start(self):
        yield self.reloadCache()

    def shutdown(self):
        self._endpoint.shutdown()
        self._endpoint = None

        self._cache = {}

    @inlineCallbacks
    def reloadCache(self):
        startTime = datetime.now(pytz.utc)
        yield DeferredList(
            [
                self._reloadCacheThread(index)
                for index in range(self._LOAD_CHUNK_PARALLELISM)
            ],
            fireOnOneErrback=True,
        )

        self._logger.info(
            "Completed loading in %s", datetime.now(pytz.utc) - startTime
        )

    @inlineCallbacks
    def _reloadCacheThread(self, threadIndex: int):
        self._cache = {}

        offset = self._LOAD_CHUNK_SIZE * threadIndex
        while True:
            startDate = datetime.now(pytz.utc)
            self._logger.info(
                "Loading %s to %s" % (offset, offset + self._LOAD_CHUNK_SIZE)
            )

            payloadJsonStr = yield self._chunkLoadRpcMethod(
                offset, self._LOAD_CHUNK_SIZE
            )

            if not payloadJsonStr:
                break

            encodedChunkTuples: List[
                ACIEncodedChunkTupleABC
            ] = yield deferToThreadWrapWithLogger(self._logger)(
                self._payloadFromJsonStrBlocking
            )(
                payloadJsonStr
            )

            self._loadDataIntoCache(encodedChunkTuples)

            offset += self._LOAD_CHUNK_SIZE * self._LOAD_CHUNK_PARALLELISM

            self._logger.info(
                "Loaded %s to %s, in %s",
                offset,
                offset + self._LOAD_CHUNK_SIZE,
                datetime.now(pytz.utc) - startDate,
            )

    def _payloadFromJsonStrBlocking(
        self, payloadJsonStr
    ) -> list[ACIEncodedChunkTupleABC]:

        return Payload().fromJsonDict(json.loads(payloadJsonStr)).tuples

    def _processChunkedIndexPayload(
        self, payloadEnvelope: PayloadEnvelope, **kwargs
    ):
        # noinspection PyTypeChecker
        chunkedIndexTuples: List[ACIEncodedChunkTupleABC] = payloadEnvelope.data
        self._loadDataIntoCache(chunkedIndexTuples)

    def _loadDataIntoCache(
        self, encodedChunkTuples: List[ACIEncodedChunkTupleABC]
    ):

        chunkKeysUpdated: List[str] = []
        deletedCount = 0
        updatedCount = 0

        for t in encodedChunkTuples:
            if not t.ckiHasEncodedData:
                if t.ckiChunkKey in self._cache:
                    deletedCount += 1
                    del self._cache[t.ckiChunkKey]
                    chunkKeysUpdated.append(t.ckiChunkKey)
                continue

            if (
                not t.ckiChunkKey in self._cache
                or self._cache[t.ckiChunkKey].ckiLastUpdate != t.ckiLastUpdate
            ):
                updatedCount += 1
                self._cache[t.ckiChunkKey] = t
                chunkKeysUpdated.append(t.ckiChunkKey)

        self._logger.debug(
            "Received %s updates from server"
            ", %s had changed"
            ", %s were deleted",
            len(encodedChunkTuples),
            updatedCount,
            deletedCount,
        )

        self._notifyOfChunkKeysUpdated(chunkKeysUpdated)

    def _notifyOfChunkKeysUpdated(self, chunkKeys: List[Any]):
        self._webAppHandler.notifyOfUpdate(chunkKeys)

    def encodedChunk(self, chunkKey) -> ACIEncodedChunkTupleABC:
        return self._cache.get(chunkKey)

    def encodedChunkKeys(self) -> List[int]:
        return list(self._cache)

    def encodedChunkLastUpdateByKey(self):
        return {g.ckiChunkKey: g.ckiLastUpdate for g in self._cache.values()}
