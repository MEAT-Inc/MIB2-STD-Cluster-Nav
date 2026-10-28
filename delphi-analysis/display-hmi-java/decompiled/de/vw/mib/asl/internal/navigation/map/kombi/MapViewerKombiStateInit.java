/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.kombi;

import de.vw.mib.asl.api.navigation.util.ASLNavigationUtilFactory;
import de.vw.mib.asl.api.navigation.util.IExtLogger;
import de.vw.mib.asl.internal.navigation.map.MapViewerUtils;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.DSIMapViewerZoomEngineFactoryVW;
import de.vw.mib.asl.internal.navigation.map.kombi.MapViewerKombiTargetHSM;
import de.vw.mib.genericevents.EventGeneric;
import de.vw.mib.genericevents.hsm.AbstractHsmState;
import de.vw.mib.genericevents.hsm.HsmState;

public class MapViewerKombiStateInit
extends AbstractHsmState {
    private static final int[] ASL_OBSERVERS = new int[]{4300048, 1074841846, 1074841845, 3499012, 3499013, 3499063, 3499064, 1074841945, 1073744781, 3499071, 1074841955, 1074841961, 1073744564};
    private static final boolean AUTOZOOM_RASTERIZING_DEFAULT = false;
    private static final int AUTOZOOM_ZOOM_LIMIT_DOWNWARDS = 30000;
    private static final int AUTOZOOM_ZOOM_LIMIT_UPWARDS = 40000;
    private static final int AUTOZOOM_LEVEL_LOW = 3000;
    private static final String LSD_SH_PARAMETER_AUTOZOOM_RASTERINZING = "de.vw.mib.asl.internal.navigation.map.kombi.autozoom_rasterizing";
    private static final String LSD_SH_PARAMETER_AUTOZOOM_ZOOMLIMIT_DOWNWARDS = "de.vw.mib.asl.internal.navigation.map.kombi.autozoom.zoomlimit_downwards";
    private static final String LSD_SH_PARAMETER_AUTOZOOM_ZOOMLIMIT_UPWARDS = "de.vw.mib.asl.internal.navigation.map.kombi.autozoom.zoomlimit_upwards";
    private static final String LSD_SH_PARAMETER_AUTOZOOM_ZOOMLEVEL_LOW = "de.vw.mib.asl.internal.navigation.map.kombi.autozoom.zoomlevel_low";
    private int[] ATTRIBUTES_MAPVIEWER_ZOOMENGINE = new int[]{3};
    private final IExtLogger logger = ASLNavigationUtilFactory.getNavigationUtilApi().getExtLogger(65536, "[MapViewerKombiTargetHSM - MapViewerKombiStateInit]");
    private final MapViewerKombiTargetHSM target;

    public MapViewerKombiStateInit(MapViewerKombiTargetHSM mapViewerKombiTargetHSM, String string, HsmState hsmState) {
        super(mapViewerKombiTargetHSM.getHsm(), string, hsmState);
        this.target = mapViewerKombiTargetHSM;
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
            case 3499012: {
                this.handleMapKombiReady();
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
            this.logger.makeTrace().append("handleDefault(receiverEventId=").append(eventGeneric.getReceiverEventId()).append(", params= ").append(eventGeneric.getParamString()).append(")").log();
        }
    }

    private void handleEntry() {
        this.logger.trace("handleEntry()");
    }

    private void handleExit() {
        this.logger.trace("handleExit()");
    }

    private void handleMapKombiReady() throws Exception {
        this.logger.trace("handleMapKombiReady()");
        this.target.datapool.setServiceMapViewerRegistred(true);
        this.target.transStateInitMapViewer();
    }

    private void handleStart() throws Exception {
        this.logger.trace("handleStart()");
        this.initAutoZoomRasterizing();
        this.initAutoZoomLevel();
        this.initASL();
        this.initDSI();
        this.initModel();
    }

    private void initASL() {
        this.logger.trace("initASL()");
        this.target.addObservers(ASL_OBSERVERS);
    }

    private void initAutoZoomLevel() {
        String string;
        String string2;
        this.logger.trace("initAutoZoomLevel()");
        int n = 40000;
        int n2 = 30000;
        int n3 = 3000;
        String string3 = System.getProperty(LSD_SH_PARAMETER_AUTOZOOM_ZOOMLIMIT_DOWNWARDS);
        if (string3 != null) {
            n2 = Integer.parseInt(string3);
            this.logger.makeInfo().append("initAutoZoomLevel - using lsd.sh parameter for autoZoomLimitDownwards, zoomLevel=").append(n2).log();
        }
        if ((string2 = System.getProperty(LSD_SH_PARAMETER_AUTOZOOM_ZOOMLIMIT_UPWARDS)) != null) {
            n = Integer.parseInt(string2);
            this.logger.makeInfo().append("initAutoZoomLevel - using lsd.sh parameter for autoZoomLimitUpwards, zoomLevel=").append(n).log();
        }
        if ((string = System.getProperty(LSD_SH_PARAMETER_AUTOZOOM_ZOOMLEVEL_LOW)) != null) {
            n3 = Integer.parseInt(string);
            this.logger.makeInfo().append("initAutoZoomLevel - using lsd.sh parameter for autozoom zoomLevelLow, zoomLevelLow=").append(n3).log();
        }
        this.target.datapool.setZoomLevelDownwards(n2);
        this.target.datapool.setZoomLevelUpwards(n);
        this.target.datapool.setZoomLevelLow(n3);
    }

    private void initAutoZoomRasterizing() {
        this.logger.trace("initAutoZoomRasterizing()");
        boolean bl = false;
        String string = System.getProperty(LSD_SH_PARAMETER_AUTOZOOM_RASTERINZING);
        if (string != null) {
            bl = Boolean.getBoolean(string);
            this.logger.makeInfo().append("initAutoZoomRasterizing - using lsd.sh parameter for autozoom rasterizing, rasterizing active=").append(bl).log();
        }
        this.target.datapool.setAutozoomRaserizing(bl);
    }

    private void initDSI() {
        this.logger.trace("initDSI()");
        DSIMapViewerZoomEngineFactoryVW.createMapViewerZoomEngine(this.target, this.ATTRIBUTES_MAPVIEWER_ZOOMENGINE);
    }

    private void initModel() {
        this.logger.trace("initModel()");
        this.target.notifierModel.notifyKombiStatusNotStarted();
    }
}

