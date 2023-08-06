import { DeviceGpsLocationTuple } from "./DeviceGpsLocationTuple";
import { Observable } from "rxjs";

export abstract class DeviceGpsLocationService {
    abstract location$: Observable<DeviceGpsLocationTuple | null>;
    abstract location: DeviceGpsLocationTuple | null;
}
