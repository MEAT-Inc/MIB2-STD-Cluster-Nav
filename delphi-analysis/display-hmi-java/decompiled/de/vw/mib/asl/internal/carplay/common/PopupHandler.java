/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.carplay.common;

import de.vw.mib.asl.framework.internal.framework.ServiceManager;
import de.vw.mib.asl.internal.carplay.common.CarPlayGlobalProperies;
import de.vw.mib.asl.internal.carplay.common.CarPlayModeHandling;
import de.vw.mib.asl.internal.carplay.target.HsmTarget;
import de.vw.mib.log4mib.LogMessage;
import de.vw.mib.popup.PopupInformationHandler;

public class PopupHandler
implements PopupInformationHandler {
    private final String classname;
    private final HsmTarget target;
    private final CarPlayGlobalProperies properties;
    private final CarPlayModeHandling modehandling;
    private boolean lastReportedPopupState;

    public PopupHandler(HsmTarget hsmTarget, CarPlayGlobalProperies carPlayGlobalProperies, CarPlayModeHandling carPlayModeHandling) {
        this.classname = "PopupInformationHandler";
        this.target = hsmTarget;
        this.properties = carPlayGlobalProperies;
        this.modehandling = carPlayModeHandling;
        this.lastReportedPopupState = carPlayGlobalProperies.isPopupOpen();
    }

    public void onPopupInformationChanged(int n) {
        if (this.target.isTraceEnabled()) {
            LogMessage logMessage = this.target.trace();
            logMessage.append("PopupInformationHandler").append(".onPopupInformationChanged(popupInfo=").append(n).append(")").log();
        }
        this.lastReportedPopupState = n == 2;
        this.target.retriggerOrStartTimer(100015, 200L, false);
    }

    public void popupTimerElapsed() {
        this.properties.setPopupOpen(this.lastReportedPopupState);
        this.checkPopupState();
    }

    public void checkPopupState() {
        LogMessage logMessage;
        boolean bl;
        boolean bl2 = bl = this.properties.isPopupOpen() || this.properties.isSdsOpen();
        if (this.target.isTraceEnabled()) {
            logMessage = this.target.trace();
            logMessage.append("PopupInformationHandler").append(".checkPopupState(popupOpen=" + this.properties.isPopupOpen() + ", SDSopen=" + this.properties.isSdsOpen() + " => isDimmed=" + bl).log();
        }
        ServiceManager.aslPropertyManager.valueChangedBoolean(2910007, bl);
        if (this.target.isTraceEnabled()) {
            logMessage = this.target.trace();
            logMessage.append("PopupInformationHandler").append(".checkPopupState: isConnected: " + this.properties.isConnected() + ", isDimed: " + bl + ", properties.isCanvasDimed()" + this.properties.isCanvasDimed() + ", properties.getCurrentScreenSource(): " + this.properties.getCurrentScreenSource() + ", properties.isCanvasVisible(): " + this.properties.isCanvasVisible() + ", properties.isVideoBorrowState(): " + this.properties.isVideoBorrowState()).log();
        }
        if (this.properties.isConnected() && bl != this.properties.isCanvasDimed()) {
            if (bl) {
                this.modehandling.borrowScreen("Borrow Screen: Popup was opended");
            } else if (!bl && this.properties.isCanvasVisible() && this.properties.isVideoBorrowState()) {
                this.modehandling.unborrowScreen("Unborrow Screen: Popup was closed");
            }
        }
        this.properties.setCanvasDimed(bl);
    }
}

