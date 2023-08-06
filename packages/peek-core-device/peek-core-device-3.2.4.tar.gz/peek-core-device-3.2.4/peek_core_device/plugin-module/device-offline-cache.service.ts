import { BehaviorSubject, interval, Observable, Subject } from "rxjs";
import { Injectable } from "@angular/core";
import { filter, takeUntil, throttle, first } from "rxjs/operators";

import {
    NgLifeCycleEvents,
    TupleSelector,
    VortexStatusService,
} from "@synerty/vortexjs";
import { DeviceTupleService } from "./_private";
import { OfflineCacheSettingTuple } from "./_private/tuples/OfflineCacheSettingTuple";
import { OfflineCacheStatusTuple } from "./tuples/OfflineCacheStatusTuple";
import { DeviceEnrolmentService } from "./device-enrolment.service";
import { DeviceInfoTuple } from "./DeviceInfoTuple";
import { OfflineCacheStatusAction } from "./_private/tuples/OfflineCacheStatusAction";

@Injectable()
export class DeviceOfflineCacheService extends NgLifeCycleEvents {
    private _offlineModeEnabled$ = new BehaviorSubject<boolean>(false);
    private _triggerCachingSubject = new BehaviorSubject<boolean>(false);
    private _cachingStatus$ = new BehaviorSubject<OfflineCacheStatusTuple[]>(
        []
    );

    private _cacheStatus = {};
    private _lastTimerId: any = null;
    private _lastTimeRun: number = 0;

    private settings = new OfflineCacheSettingTuple();
    private deviceInfo: DeviceInfoTuple = new DeviceInfoTuple();

    private unsub = new Subject<void>();

    // private pauseCacheForGarbageCollectorInterval$: Observable<number>;
    private cachingPausedForGarbageCollector$ = new BehaviorSubject<boolean>(
        false
    );

    constructor(
        private vortexStatusService: VortexStatusService,
        private tupleService: DeviceTupleService,
        private enrolmentService: DeviceEnrolmentService
    ) {
        super();
        const CACHE_RUN_SECONDS = 60;
        const CACHE_PAUSE_SECONDS = 0;

        // JJC, This is no longer required for garbage collection
        // but i'd like to keep the integrated APIs.
        // this.pauseCacheForGarbageCollectorInterval$ = interval(
        //     (CACHE_RUN_SECONDS + CACHE_PAUSE_SECONDS) * 1000
        // );
        // this.pauseCacheForGarbageCollectorInterval$
        //     .pipe(takeUntil(this.onDestroyEvent))
        //     .subscribe(() => {
        //         console.log(`${new Date()} Pausing load for garbage collector`);
        //         this.cachingPausedForGarbageCollector$.next(true);
        //         setTimeout(() => {
        //             console.log(
        //                 `${new Date()} Resuming load` +
        //                     " after we hope the garbage collector ran"
        //             );
        //             this.cachingPausedForGarbageCollector$.next(false);
        //         }, CACHE_PAUSE_SECONDS * 1000);
        //     });

        // Why should we care if we're enrolled or not to check for updates?
        // Devices that are not enrolled should not be able to access any thing on
        // the servers.
        this.enrolmentService
            .deviceInfoObservable()
            .subscribe((deviceInfo: DeviceInfoTuple) => {
                this.deviceInfo = deviceInfo;
                this.unsub.next();
                const tupleSelector = new TupleSelector(
                    OfflineCacheSettingTuple.tupleName,
                    { deviceToken: deviceInfo.deviceToken }
                );

                // This is an application permanent subscription
                this.tupleService.offlineObserver
                    .subscribeToTupleSelector(tupleSelector)
                    .pipe(takeUntil(this.unsub))
                    .subscribe((tuples: OfflineCacheSettingTuple[]) => {
                        if (tuples.length === 0) return;

                        const oldSettings = this.settings;
                        this.settings = tuples[0];

                        if (this.settings.offlineEnabled) {
                            if (
                                !oldSettings.offlineEnabled ||
                                this.settings.offlineCacheSyncSeconds !==
                                    oldSettings.offlineCacheSyncSeconds
                            )
                                this._resetTimer();
                        }

                        if (
                            this.settings.offlineEnabled !==
                            this._offlineModeEnabled$.getValue()
                        ) {
                            this._offlineModeEnabled$.next(
                                this.settings.offlineEnabled
                            );
                        }
                    });
            });

        vortexStatusService.isOnline
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(() => {
                this._resetTimer();
            });

        this.cacheStatus$ //
            .pipe(
                throttle((val) => interval(60000)),
                filter(() => this.vortexStatusService.snapshot.isOnline)
            )
            .subscribe(() => {
                const action = new OfflineCacheStatusAction();
                action.deviceToken = this.deviceInfo.deviceToken;
                action.cacheStatusList = this._cacheStatusList;
                this.tupleService.tupleAction
                    .pushAction(action)
                    .then(() =>
                        console.log("Offine cache status sent successfully")
                    )
                    .catch((e) => console.log(`ERROR: ${e}`));
            });
    }

    private _resetTimer(): void {
        if (this._lastTimerId != null) {
            clearInterval(this._lastTimerId);
            this._lastTimerId = null;
        }

        if (!this.settings.offlineEnabled) return;

        console.assert(
            this.settings.offlineCacheSyncSeconds > 30,
            "Cache time is too small"
        );

        this._lastTimerId = setInterval(
            () => this._triggerUpdate(),
            this.settings.offlineCacheSyncSeconds * 1000
        );
        this._triggerUpdate();

        /*
         // Check for updates every so often
         Observable.interval(this.OFFLINE_CHECK_PERIOD_MS)
         .pipe(takeUntil(this.onDestroyEvent))
         .subscribe(() => this.askServerForUpdates())
         */
    }

    private _triggerUpdate(): void {
        // Force an update if the trigger has changed state
        // This condition occurs when the services are starting
        // and offline mode is enabled.
        const force =
            this._triggerCachingSubject.getValue() != this.offlineModeEnabled;
        if (!force && !this.vortexStatusService.snapshot.isOnline) return;
        const timeSinceLastRun =
            new Date().getTime() / 1000 - this._lastTimeRun;
        if (timeSinceLastRun < this.settings.offlineCacheSyncSeconds) {
            console.log("Skipping this cache cycle, it's too soon");
            return;
        }
        this._triggerCachingSubject.next(true);
    }

    get triggerCachingObservable(): Observable<boolean> {
        return this._triggerCachingSubject.asObservable();
    }

    updateCachingStatus(status: OfflineCacheStatusTuple): void {
        this._cacheStatus[status.key] = status;
        this._cachingStatus$.next(this._cacheStatusList);
    }

    async waitForGarbageCollector(): Promise<void> {
        if (this.cachingPausedForGarbageCollector$.getValue()) {
            await new Promise<void>((resolve, reject) => {
                this.cachingPausedForGarbageCollector$
                    .pipe(
                        filter((paused) => paused === false),
                        first()
                    )
                    .subscribe(() => resolve());
            });
        }
    }

    private get _cacheStatusList(): OfflineCacheStatusTuple[] {
        return Object.keys(this._cacheStatus)
            .sort((one, two) => (one > two ? -1 : 1))
            .map((k) => this._cacheStatus[k]);
    }

    get cacheStatus$(): BehaviorSubject<OfflineCacheStatusTuple[]> {
        return this._cachingStatus$;
    }

    get offlineModeEnabled(): boolean {
        return this.settings.offlineEnabled;
    }

    get offlineModeEnabled$(): Observable<boolean> {
        return this._offlineModeEnabled$;
    }

    get cachingEnabled(): boolean {
        return (
            this.settings.offlineEnabled &&
            this.vortexStatusService.snapshot.isOnline
        );
    }
}
