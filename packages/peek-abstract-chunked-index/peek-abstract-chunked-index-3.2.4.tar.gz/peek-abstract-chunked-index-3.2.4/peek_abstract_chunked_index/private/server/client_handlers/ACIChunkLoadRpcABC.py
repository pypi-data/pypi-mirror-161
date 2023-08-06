import json
from abc import ABCMeta
from typing import Any
from typing import List
from typing import Optional
from typing import Type

from sqlalchemy import select
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import Select
from vortex.Payload import Payload

from peek_abstract_chunked_index.private.tuples.ACIEncodedChunkTupleABC import (
    ACIEncodedChunkTupleABC,
)
from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_base.storage.RunPyInPg import runPyInPgBlocking


class ACIChunkLoadRpcABC(metaclass=ABCMeta):
    def __init__(self, dbSessionCreator: DbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    # -------------
    def ckiInitialLoadChunksPayloadBlocking(
        self,
        offset: int,
        count: int,
        Declarative: Type[ACIEncodedChunkTupleABC],
        sql: Optional[Select] = None,
    ) -> str:
        """Chunked Key Index - Initial Load Chunks Blocking

        This method is used to load the initial set of chunks from the server
        to the client.

        """

        if sql is None:
            table = Declarative.__table__
            sql = (
                select([table])
                .order_by(Declarative.sqlCoreChunkKeyColumn())
                .offset(offset)
                .limit(count)
            )

        sqlStr = str(
            sql.compile(
                dialect=postgresql.dialect(),
                compile_kwargs={"literal_binds": True},
            )
        )

        sqlCoreLoadModStr = ".".join(
            [Declarative.__module__, Declarative.__name__]
        )

        return runPyInPgBlocking(
            self._dbSessionCreator,
            self._load,
            classMethodToImportTuples=None,
            sqlCoreLoadModStr=sqlCoreLoadModStr,
            sqlStr=sqlStr,
            fetchSize=count,
        )

    @classmethod
    def _load(cls, plpy, sqlStr, sqlCoreLoadModStr, fetchSize):

        from importlib.util import find_spec

        modName, className = sqlCoreLoadModStr.rsplit(".", 1)

        import sys

        if modName in sys.modules:
            package_ = sys.modules[modName]

        else:
            modSpec = find_spec(modName)
            if not modSpec:
                raise Exception(
                    "Failed to find package %s,"
                    " is the python package installed?" % modName
                )

            package_ = modSpec.loader.load_module()

        TupleClass = getattr(package_, className)
        tupleLoaderMethod = TupleClass.sqlCoreLoad

        # ---------------
        # Turn a row["val"] into a row.val
        class Wrap:
            row = None

            def __getattr__(self, name):
                return self.row[name]

        wrap = Wrap()

        # ---------------
        # Iterate through and load the tuples
        results = []

        cursor = plpy.cursor(sqlStr)
        while True:
            rows = cursor.fetch(max(500, fetchSize))
            if not rows:
                break
            for row in rows:
                wrap.row = row
                results.append(tupleLoaderMethod(wrap))

        return (
            json.dumps(Payload(tuples=results).toJsonDict())
            if results
            else None
        )
