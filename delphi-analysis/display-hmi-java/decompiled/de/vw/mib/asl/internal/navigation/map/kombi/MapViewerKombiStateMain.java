/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.kombi;

import de.vw.mib.asl.api.navbap.ASLNavBAPFactory;
import de.vw.mib.asl.api.navigation.map.ASLNavigationMapAPI;
import de.vw.mib.asl.api.navigation.map.ASLNavigationMapFactory;
import de.vw.mib.asl.api.navigation.util.ASLNavigationUtilFactory;
import de.vw.mib.asl.api.navigation.util.IExtLogger;
import de.vw.mib.asl.api.navigation.util.factoryreset.FactoryResetParticipantWithCallback;
import de.vw.mib.asl.api.navigation.util.factoryreset.TargetForResetNavigation;
import de.vw.mib.asl.api.system.ASLSystemFactory;
import de.vw.mib.asl.framework.internal.framework.ServiceManager;
import de.vw.mib.asl.internal.navigation.map.FPKMapScaleUtils;
import de.vw.mib.asl.internal.navigation.map.MapViewerUtils;
import de.vw.mib.asl.internal.navigation.map.dsi.datapool.MapDataPool;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.DSIMapViewerControlFactoryVW;
import de.vw.mib.asl.internal.navigation.map.kombi.MapViewerKombiTargetHSM;
import de.vw.mib.genericevents.EventGeneric;
import de.vw.mib.genericevents.GenericEventException;
import de.vw.mib.genericevents.hsm.AbstractHsmState;
import de.vw.mib.genericevents.hsm.HsmState;

public class MapViewerKombiStateMain
extends AbstractHsmState
implements TargetForResetNavigation {
    private final IExtLogger logger = ASLNavigationUtilFactory.getNavigationUtilApi().getExtLogger(65536, "[MapViewerKombiTargetHSM - MapViewerKombiStateMain]");
    private final MapViewerKombiTargetHSM target;
    final ASLNavigationMapAPI map;
    final MapDataPool datapool;
    private FactoryResetParticipantWithCallback navigationResetParticipant;

    public MapViewerKombiStateMain(MapViewerKombiTargetHSM mapViewerKombiTargetHSM, String string, HsmState hsmState) {
        super(mapViewerKombiTargetHSM.getHsm(), string, hsmState);
        this.target = mapViewerKombiTargetHSM;
        this.map = ASLNavigationMapFactory.getNavigationMapApi();
        this.datapool = DSIMapViewerControlFactoryVW.getMapDatapoolMain();
    }

    public HsmState dsiMapViewerZoomEngineUpdateRecommendedZoom(float f, int n) throws Exception {
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("dsiMapViewerZoomEngineUpdateRecommendedZoom(recommendedZoom=").append(f).append(")").log();
        }
        if (this.target.datapool.isAutozoomRaserizing()) {
            f = this.target.rasterizeZoomLevel(f);
        }
        f = MapViewerUtils.checkZoomLevelIsInRange(f);
        if (this.target.datapool.getRecommendedZoom() == f) {
            this.logger.trace("the value has not been changed");
            return null;
        }
        this.target.datapool.setRecommendedZoom(f);
        if (this.target.isStateVisbileActive() && this.target.datapool.isAutozoomActive()) {
            int n2 = MapViewerUtils.calculateZoomLevelNormalized(f);
            this.target.datapool.setZoomLevel(n2 * 100);
            MapViewerKombiStateMain.updateMapScaleInBAP(n2, true);
            this.target.notifierDSI.setZoomLevel(f);
        }
        return null;
    }

    public HsmState handle(EventGeneric eventGeneric) throws Exception {
        switch (eventGeneric.getReceiverEventId()) {
            case 2: {
                this.handleEntry();
                break;
            }
            case 3: {
                this.handleStart();
                break;
            }
            case 4: {
                this.handleExit();
                break;
            }
            case 4300048: {
                this.handleDistanceUnitChanged(eventGeneric);
                break;
            }
            case 3499013: {
                this.handleMapKombiNotReady();
                break;
            }
            case 1074841846: {
                this.handleMapKombiSetInvisible();
                break;
            }
            case 1074841845: {
                this.handleMapKombiSetVisible();
                break;
            }
            case 3499063: {
                this.handleSpeechRecognizerActive();
                break;
            }
            case 12: {
                this.handleMonitorServiceRegistered(eventGeneric);
                break;
            }
            case 13: {
                this.handleMonitorServiceUnregistered(eventGeneric);
                break;
            }
            case 1074841945: {
                this.handleASLNavigationMapSetupSetFPKMapPerspective(eventGeneric);
                break;
            }
            case 1073744781: {
                this.handleASLNavigationMapSetupShowTrafficIncidents(eventGeneric);
                break;
            }
            case 3499071: {
                this.handleASLNavigationMapAPIForwardTrafficVisibility(eventGeneric);
                break;
            }
            case 1074841955: {
                this.handleDayNightMode(eventGeneric);
                break;
            }
            case 1074841961: {
                this.handleSetVICSTrafficFlowType(eventGeneric);
                break;
            }
            default: {
                this.handleDefault(eventGeneric);
                return this.myParent;
            }
        }
        return null;
    }

    private void handleDayNightMode(EventGeneric eventGeneric) throws GenericEventException {
        int n = eventGeneric.getInt(0);
        this.target.setSelectedDayNightMode(n);
    }

    private void handleDefault(EventGeneric eventGeneric) {
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("handleDefault(receiverEventId=").append(eventGeneric.getReceiverEventId()).append(", params= ").append(eventGeneric.getParamString()).append(")").log();
        }
    }

    private void handleDistanceUnitChanged(EventGeneric eventGeneric) throws GenericEventException {
        this.logger.trace("handleDistanceUnitChanged()");
        int n = eventGeneric.getInt(0);
        if (n == 0) {
            this.target.notifierDSI.setMetricSystem(2);
        } else if (n == 1) {
            if (ServiceManager.configManagerDiag.isFeatureFlagSet(155)) {
                this.target.notifierDSI.setMetricSystem(3);
            } else {
                this.target.notifierDSI.setMetricSystem(4);
            }
        } else {
            this.logger.error("handleSetDsiDistanceUnit() invalid distance unit");
        }
        float f = this.target.datapool.getRecommendedZoom();
        f = MapViewerUtils.checkZoomLevelIsInRange(f);
        if (!this.target.datapool.isAutozoomActive()) {
            f = this.target.datapool.getZoomLevel();
        }
        MapViewerKombiStateMain.updateMapScaleInBAP(MapViewerUtils.calculateZoomLevelNormalized(f), this.target.datapool.isAutozoomActive());
    }

    private void handleEntry() {
        this.logger.trace("handleEntry()");
        if (this.navigationResetParticipant == null) {
            this.navigationResetParticipant = ASLNavigationUtilFactory.getNavigationUtilApi().createFactoryResetParticipantForNavigationDomainAndAddToService(this);
        }
    }

    private void handleExit() {
        this.logger.trace("handleExit()");
        if (this.navigationResetParticipant != null) {
            ASLNavigationUtilFactory.getNavigationUtilApi().removeNavigationResetParticipantFromService(this.navigationResetParticipant);
            this.navigationResetParticipant = null;
        }
    }

    private void handleMapKombiNotReady() throws Exception {
        this.logger.trace("handleMapKombiNotReady()");
        this.target.datapool.setServiceMapViewerRegistred(false);
        if (this.target.isStateVisbileActive()) {
            this.target.datapool.setMapViewerVisibleAfterKombiRestartFinished(true);
        }
        this.target.transStateRestart();
    }

    private void handleMapKombiSetInvisible() throws Exception {
        this.logger.trace("handleMapKombiSetInvisible()");
        this.target.transStateInvisible();
    }

    private void handleMapKombiSetVisible() throws Exception {
        this.logger.trace("handleMapKombiSetVisible()");
        this.target.transStateVisible();
    }

    private void handleSpeechRecognizerActive() throws Exception {
        this.logger.makeInfo().append("handleSpeechRecognitionActive()").log();
        if (this.target.isStateVisbileActive() || this.target.isStateContinuousZoomActive()) {
            this.target.datapool.setMapViewerVisibleAfterRecognizerFinished(true);
        } else if (this.target.isStateInvisbileActive()) {
            this.target.datapool.setMapViewerVisibleAfterRecognizerFinished(false);
        }
        this.target.transStateSpeechRecognizerActive();
    }

    private void handleMonitorServiceRegistered(EventGeneric eventGeneric) throws GenericEventException {
    }

    private void handleMonitorServiceUnregistered(EventGeneric eventGeneric) throws GenericEventException {
    }

    private void handleStart() {
        this.logger.trace("handleStart()");
    }

    private void handleASLNavigationMapSetupSetFPKMapPerspective(EventGeneric eventGeneric) throws GenericEventException {
        int n = eventGeneric.getInt(0);
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("handleASLNavigationMapSetupSetFPKMapPerspective( perspective = ").append(n).append(" )").log();
        }
        this.target.setMapInKombiPerspective(n);
    }

    private void handleASLNavigationMapSetupShowTrafficIncidents(EventGeneric eventGeneric) throws GenericEventException {
        boolean bl = eventGeneric.getBoolean(0);
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("handleASLNavigationMapSetupShowTrafficIncidents( visible = ").append(bl).append(" )").log();
        }
        this.target.notifierDSI.showTMCMessages(bl);
    }

    private void handleASLNavigationMapAPIForwardTrafficVisibility(EventGeneric eventGeneric) throws GenericEventException {
        boolean bl = eventGeneric.getBoolean(0);
        boolean bl2 = eventGeneric.getBoolean(1);
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("handleASLNavigationMapAPIForwardTrafficVisibility(congestion =  ").append(bl).append(", freeFlow =  ").append(bl2).append(" )").log();
        }
        this.target.notifierDSI.showSpeedAndFlowCongestions(bl);
        this.target.notifierDSI.showSpeedAndFlowFreeFlow(bl2);
    }

    private void handleSetVICSTrafficFlowType(EventGeneric eventGeneric) throws GenericEventException {
        int n = eventGeneric.getInt(0);
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("handleSetVICSTrafficFlowType(").append(n).append(")").log();
        }
        switch (n) {
            case 0: {
                this.target.notifierDSI.setSpeedAndFlowRoadClass(4);
                break;
            }
            case 1: {
                this.target.notifierDSI.setSpeedAndFlowRoadClass(1);
                break;
            }
            case 2: {
                this.target.notifierDSI.setSpeedAndFlowRoadClass(2);
                break;
            }
            case 3: {
                this.target.notifierDSI.setSpeedAndFlowRoadClass(3);
                break;
            }
            default: {
                this.target.notifierDSI.setSpeedAndFlowRoadClass(3);
            }
        }
    }

    public void handleNavigationSettingsReset() throws Exception {
        this.logger.trace("handleResetNavigationSettings()");
        this.target.setPerspective3D();
        if (ServiceManager.configManagerDiag.isFeatureFlagSet(472)) {
            this.target.notifierDSI.setSpeedAndFlowRoadClass(3);
        }
        this.navigationResetParticipant.notifyResetDone();
    }

    static void updateMapScaleInBAP(int n, boolean bl) {
        int n2 = bl ? 1 : 0;
        FPKMapScaleUtils.ZoomLevelThreshold zoomLevelThreshold = FPKMapScaleUtils.getFPKMapScaleThreshold(n);
        switch (ASLSystemFactory.getSystemApi().getConfiguredDistanceUnit()) {
            case 1: {
                ASLNavBAPFactory.getNavBAPApi().updateMapsScale(zoomLevelThreshold.zoomImperial, zoomLevelThreshold.unitImperial, n2);
                break;
            }
            case 0: {
                ASLNavBAPFactory.getNavBAPApi().updateMapsScale(zoomLevelThreshold.zoomMetric, zoomLevelThreshold.unitMetric, n2);
                break;
            }
        }
    }
}

