import { Component, OnInit } from "@angular/core";
import {
    NgLifeCycleEvents,
    Payload,
    PayloadEnvelope,
    VortexService,
} from "@synerty/vortexjs";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
// import { FileUploader } from "ng2-file-upload"
import {
    CreateDeviceUpdateAction,
    DeviceUpdateTuple,
} from "@peek/peek_core_device/_private";

@Component({
    selector: "core-device-upload-device-update",
    templateUrl: "./upload-device-update.component.html",
})
export class UploadDeviceUpdateComponent
    extends NgLifeCycleEvents
    implements OnInit
{
    newUpdate: DeviceUpdateTuple = new DeviceUpdateTuple();
    serverRestarting: boolean = false;
    progressPercentage: string = "";
    // uploader: FileUploader = null
    hasBaseDropZoneOver: boolean = false;
    private readonly filt = {
        plugin: "peek_logic_service",
        key: "peek_logic_service.plugin.version.info",
    };

    constructor(
        private vortexService: VortexService,
        private balloonMsg: BalloonMsgService
    ) {
        super();

        // Subscribe to the angular check event
        // this.doCheckEvent.subscribe(() => this.checkProgress());
    }

    ngOnInit() {}

    /*
    formEnabled(): boolean {
        return this.uploader == null
    }
    
    uploadEnabled() {
        return this.uploader != null
    }
    
    isFormValid(): boolean {
        let isValidStr = v => v != null && v.length > 0
        let isValidVersion = v => v != null && v.length > 0
        return isValidStr(this.newUpdate.deviceType)
            && isValidStr(this.newUpdate.description)
            && isValidVersion(this.newUpdate.appVersion)
            && isValidVersion(this.newUpdate.updateVersion)
    }
    
    nextClicked() {
        if (!this.isFormValid()) {
            this.balloonMsg.showWarning("The information you've provided is incomplete")
            return
        }
        
        let action = new CreateDeviceUpdateAction()
        action.newUpdate = this.newUpdate
        
        new Payload({}, [action])
            .makePayloadEnvelope()
            .then((payloadEnvelope: PayloadEnvelope) => payloadEnvelope.toVortexMsg())
            .then((vortexMsg: string) => {
                let data = encodeURIComponent(vortexMsg)
                
                this.uploader = new FileUploader({
                    url: "/peek_core_device/create_device_update?payload=" + data,
                    isHTML5: true,
                    disableMultipart: true,
                    queueLimit: 1,
                    method: "POST",
                    autoUpload: true,
                    removeAfterUpload: false
                })
            })
        
    }
    
    checkProgress() {
        if (!this.uploadEnabled())
            return
        
        this.progressPercentage = ""
        
        if (this.uploader.queue.length != 1)
            return
        
        let fileItem = this.uploader.queue[0]
        if (fileItem._xhr == null)
            return
        
        let status = fileItem._xhr.status
        let responseJsonStr = fileItem._xhr.responseText
        
        if (!status || status == 200 && !responseJsonStr.length) {
            this.progressPercentage = fileItem.progress + "%"
            return
        }
        
        if (status == 200) {
            let data = JSON.parse(responseJsonStr)
            
            this.progressPercentage = ""
            if (data.error) {
                this.balloonMsg.showError("Upload Failed\n" + data.error)
            }
            else {
                this.serverRestarting = true
                this.balloonMsg.showSuccess("Upload Complete\n" + data.message)
            }
            
        }
        else {
            this.progressPercentage = ""
            this.balloonMsg.showError("Upload failed\nStatus : " + status)
        }
        
        this.uploader.removeFromQueue(fileItem)
        this.uploader = null
    }
    
    fileOverBase(e: any): void {
        this.hasBaseDropZoneOver = e
    }
     */
}
