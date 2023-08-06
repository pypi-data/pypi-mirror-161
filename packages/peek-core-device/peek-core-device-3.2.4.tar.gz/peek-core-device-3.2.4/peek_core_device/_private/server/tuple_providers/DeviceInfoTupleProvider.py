import logging
from typing import Union

from peek_core_device._private.server.controller.OfflineCacheController import (
    OfflineCacheController,
)
from peek_core_device._private.storage.DeviceInfoTable import DeviceInfoTable
from peek_core_device._private.storage.GpsLocationTable import GpsLocationTable
from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class DeviceInfoTupleProvider(TuplesProviderABC):
    def __init__(
        self, ormSessionCreator, offlineCacheController: OfflineCacheController
    ):
        self._ormSessionCreator = ormSessionCreator
        self._offlineCacheController = offlineCacheController

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(
        self, filt: dict, tupleSelector: TupleSelector
    ) -> Union[Deferred, bytes]:

        deviceId = tupleSelector.selector.get("deviceId")

        ormSession = self._ormSessionCreator()
        try:
            query = ormSession.query(
                DeviceInfoTable, GpsLocationTable
            ).outerjoin(GpsLocationTable)

            if deviceId is not None:
                query = query.filter(DeviceInfoTable.deviceId == deviceId)

            tuples = []
            for deviceInfoTableRow, gpsLocationTableRow in query.all():
                tuples.append(
                    deviceInfoTableRow.toTuple(
                        currentLocationTuple=gpsLocationTableRow,
                        lastCacheCheck=self._offlineCacheController.lastCacheUpdate(
                            deviceInfoTableRow.deviceToken
                        ),
                    )
                )

            # Create the vortex message
            return (
                Payload(filt, tuples=tuples).makePayloadEnvelope().toVortexMsg()
            )

        finally:
            ormSession.close()
