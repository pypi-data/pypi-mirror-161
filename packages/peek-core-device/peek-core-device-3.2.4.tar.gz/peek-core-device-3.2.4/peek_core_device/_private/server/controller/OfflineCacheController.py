import logging
from collections import defaultdict
from datetime import datetime
from typing import List
from typing import Optional

from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Tuple import Tuple
from vortex.TupleAction import TupleActionABC

from peek_core_device._private.server.controller.NotifierController import (
    NotifierController,
)
from peek_core_device._private.storage.DeviceInfoTable import DeviceInfoTable
from peek_core_device._private.tuples.OfflineCacheStatusAction import (
    OfflineCacheStatusAction,
)
from peek_core_device._private.tuples.OfflineCacheStatusTuple import (
    OfflineCacheStatusTuple,
)
from peek_core_device._private.tuples.UpdateOfflineCacheSettingAction import (
    UpdateOfflineCacheSettingAction,
)

logger = logging.getLogger(__name__)


class OfflineCacheController:
    def __init__(self, dbSessionCreator):
        self._dbSessionCreator = dbSessionCreator
        self._notifierController = None

        self._lastUpdateByDeviceToken = {}
        self._lastStatusByDeviceToken = defaultdict(list)

    def setNotificationController(self, notifierController: NotifierController):
        self._notifierController = notifierController

    def lastCacheUpdate(self, deviceToken: str) -> Optional[datetime]:
        return self._lastUpdateByDeviceToken.get(deviceToken)

    def lastCacheStatus(
        self, deviceToken: str
    ) -> dict[str : list[OfflineCacheStatusTuple]]:
        return self._lastStatusByDeviceToken.get(deviceToken)

    def shutdown(self):
        self._lastUpdateByDeviceToken = {}

    def processTupleAction(self, tupleAction: TupleActionABC) -> List[Tuple]:

        if isinstance(tupleAction, UpdateOfflineCacheSettingAction):
            return self._processOfflineCacheSettingUpdate(tupleAction)

        if isinstance(tupleAction, OfflineCacheStatusAction):
            return self._processOfflineCacheStatusUpdate(tupleAction)

    @deferToThreadWrapWithLogger(logger)
    def _processOfflineCacheSettingUpdate(
        self, action: UpdateOfflineCacheSettingAction
    ) -> List[Tuple]:
        """Process Offline Cache Update

        :rtype: Deferred
        """
        ormSession = self._dbSessionCreator()
        try:
            # There should only be one item that exists if it exists.
            deviceInfo = (
                ormSession.query(DeviceInfoTable)
                .filter(DeviceInfoTable.id == action.deviceInfoId)
                .one()
            )

            # There should one be one
            deviceInfo.isOfflineCacheEnabled = action.offlineCacheEnabled

            ormSession.commit()

            self._notifierController.notifyDeviceOfflineCacheSetting(
                deviceToken=deviceInfo.deviceToken
            )

            return []

        finally:
            # Always close the session after we create it
            ormSession.close()

    @deferToThreadWrapWithLogger(logger)
    def _processOfflineCacheStatusUpdate(
        self, action: OfflineCacheStatusAction
    ) -> List[Tuple]:
        lastDate = min([s.lastCheckDate for s in action.cacheStatusList])
        self._lastUpdateByDeviceToken[action.deviceToken] = lastDate
        self._lastStatusByDeviceToken[
            action.deviceToken
        ] = action.cacheStatusList
        return []
