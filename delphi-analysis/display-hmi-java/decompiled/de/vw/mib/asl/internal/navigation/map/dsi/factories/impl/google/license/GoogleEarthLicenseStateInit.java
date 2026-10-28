/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.google.license;

import de.vw.mib.asl.api.navigation.util.ASLNavigationUtilFactory;
import de.vw.mib.asl.api.navigation.util.IExtLogger;
import de.vw.mib.asl.api.online.ASLOnlineFactory;
import de.vw.mib.asl.api.online.ASLOnlineServiceListener;
import de.vw.mib.asl.framework.internal.framework.ServiceManager;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.DSIMapViewerGoogleCtrlFactoryVW;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.google.license.GoogleEarthLicenseTargetHSM;
import de.vw.mib.genericevents.EventGeneric;
import de.vw.mib.genericevents.hsm.AbstractHsmState;
import de.vw.mib.genericevents.hsm.Hsm;
import de.vw.mib.genericevents.hsm.HsmState;

public final class GoogleEarthLicenseStateInit
extends AbstractHsmState {
    private static final int[] ASL_OBSERVERS = new int[]{4800009, 3499018, 3499019, 3499095, 3499096, 1073744487};
    protected final IExtLogger logger = ASLNavigationUtilFactory.getNavigationUtilApi().getExtLogger(65536, "[GoogleEarthLicenseStateInit]");
    protected final GoogleEarthLicenseTargetHSM target;
    protected int licenceDelayTimerRetryCount = 0;
    private final int LICENSE_DELAY_TIMER_MAX_RETRIES;
    protected static final int GE_LICENCE_CHECK_DELAY_1_MINUTE = 60000;
    private boolean licenseCheckDone = false;

    public GoogleEarthLicenseStateInit(GoogleEarthLicenseTargetHSM googleEarthLicenseTargetHSM, Hsm hsm, String string, HsmState hsmState) {
        super(hsm, string, hsmState);
        this.LICENSE_DELAY_TIMER_MAX_RETRIES = 2;
        this.target = googleEarthLicenseTargetHSM;
        googleEarthLicenseTargetHSM.setGoogleEarthServiceID(ASLOnlineFactory.getOnlineCoreServices().getServiceIDWithNumericServiceID(14));
    }

    public HsmState handle(EventGeneric eventGeneric) throws Exception {
        switch (eventGeneric.getReceiverEventId()) {
            case 2: {
                this.handleEntry();
                break;
            }
            case 4: {
                this.handleExit();
                break;
            }
            case 3: {
                this.handleStart();
                break;
            }
            case 4800009: {
                this.handleASLOnlineServiceListNotification();
                break;
            }
            case 3499095: {
                this.handleMapSwitcherReady();
                break;
            }
            case 3499018: {
                this.handleMapInstanceGoogleEarthReady();
                break;
            }
            case 3499019: {
                this.handleMapInstanceGoogleEarthNotReady();
                break;
            }
            case 3499096: {
                this.doLicenseCheck();
                break;
            }
            default: {
                this.handleDefault(eventGeneric);
                return this.myParent;
            }
        }
        return null;
    }

    private void handleDefault(EventGeneric eventGeneric) {
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("handleDefault(): ev.Id=").append(eventGeneric.getReceiverEventId()).append(" Params=").append(eventGeneric.getParamString()).log();
        }
    }

    private void handleEntry() {
        this.logger.trace("handleEntry()");
    }

    private void handleExit() {
        this.logger.trace("handleExit()");
    }

    private void handleStart() throws Exception {
        this.logger.trace("handleStart()");
        this.initModel();
        this.initDSI();
        this.initASL();
    }

    private void initASL() {
        this.logger.trace("initASL()");
        this.target.addObservers(ASL_OBSERVERS);
    }

    private void initDSI() {
        this.logger.trace("initDSI()");
        this.target.notifierDSI.setDsiMapViewerGoogleCtrl(DSIMapViewerGoogleCtrlFactoryVW.createMapViewerGoogleCtrl(this.target, null));
    }

    private void initModel() {
        this.target.notifierModel.notifyGoogleEarthNotAvailable();
    }

    private void handleASLOnlineServiceListNotification() throws Exception {
        boolean bl = ASLOnlineFactory.getOnlineCoreServices().isServiceAvailable(this.target.getGoogleEarthServiceID());
        this.target.setGoogleAvailableInServiceList(bl);
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("handleASLOnlineServiceListNotification ( googleAvailable = ").append(bl).append(" )").log();
        }
        if (!bl) {
            this.disableGoogleEarthLastModeAndStayOnOnboardMap();
        } else {
            this.checkGoogleState();
        }
    }

    private void handleMapSwitcherReady() throws Exception {
        this.logger.trace("handleMapSwitcherReady");
        this.target.setMapSwitcherReady(true);
        this.checkGoogleState();
    }

    private void handleMapInstanceGoogleEarthNotReady() throws Exception {
        this.logger.trace("handleMapInstanceGoogleEarthNotReady");
        this.target.setMapViewerReady(false);
        this.checkGoogleState();
    }

    private void handleMapInstanceGoogleEarthReady() throws Exception {
        this.logger.trace("handleMapInstanceGoogleEarthReady");
        this.target.setMapViewerReady(true);
        this.checkGoogleState();
    }

    private void checkGoogleState() {
        if (this.target.isMapViewerReady() && this.target.isMapSwitcherReady() && this.target.isGoogleAvailableInServiceList()) {
            if (this.target.datapool.getMainMapMapTypeLast() == 1 && !this.licenseCheckDone) {
                this.logger.trace("Everything's ready but Google was last mode so we will wait for license check.");
                this.doLicenseCheck();
            } else {
                this.logger.trace("all conditions meet, GoogleEarth is being enabled");
                this.showGoogleEarthButton();
            }
        }
    }

    private void doLicenseCheck() {
        ASLOnlineFactory.getOnlineCoreServices().checkOnlineServiceStatus(this.target.getGoogleEarthServiceID(), new ASLOnlineServiceListener(){

            public void updateServiceStatusOnChange(int n) {
                if (n == 0) {
                    GoogleEarthLicenseStateInit.this.licenceDelayTimerRetryCount = 0;
                    GoogleEarthLicenseStateInit.this.licenseCheckDone = true;
                    GoogleEarthLicenseStateInit.this.checkGoogleState();
                } else if (GoogleEarthLicenseStateInit.this.licenceDelayTimerRetryCount < 2) {
                    ++GoogleEarthLicenseStateInit.this.licenceDelayTimerRetryCount;
                    EventGeneric eventGeneric = ServiceManager.eventMain.getEventFactory().newEvent(GoogleEarthLicenseStateInit.this.target.getTargetId(), GoogleEarthLicenseStateInit.this.target.getTargetId(), 3499096);
                    GoogleEarthLicenseStateInit.this.target.startTimer(eventGeneric, 60000L, false);
                } else {
                    GoogleEarthLicenseStateInit.this.licenceDelayTimerRetryCount = 0;
                    GoogleEarthLicenseStateInit.this.disableGoogleEarthLastModeAndStayOnOnboardMap();
                }
            }
        });
    }

    void disableGoogleEarthLastModeAndStayOnOnboardMap() {
        this.logger.trace("disableGoogleEarthLastModeAndStayOnOnboardMap()");
        this.target.datapool.setMainMapLastMapType(0);
        this.target.notifierDSI.setConnectionInformationForbidden();
        this.target.notifierModel.notifyLastMapTypeOnboard();
        this.target.notifierModel.notifyMapTypeCurrentOnboard();
        this.target.notifierModel.notifyGoogleEarthNotAvailable();
        try {
            this.target.transStateWork();
        }
        catch (Exception exception) {
            this.logger.error("Exception in disableGoogleEarthLastModeAndStayOnOnboardMap()");
        }
    }

    private void showGoogleEarthButton() {
        this.target.datapool.setConnectionStateAllow(true);
        this.target.notifierDSI.setConnectionInformationAllow();
        this.target.notifierModel.notifyGoogleEarthAvailable();
        try {
            this.target.transStateWork();
        }
        catch (Exception exception) {
            this.logger.error("Exception in showGoogleEarthButton()");
        }
    }
}

