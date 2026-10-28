/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.mainmap.mapswitch;

import de.vw.mib.asl.api.navigation.map.ASLNavigationMapFactory;
import de.vw.mib.asl.api.navigation.util.ASLNavigationUtilFactory;
import de.vw.mib.asl.api.navigation.util.IExtLogger;
import de.vw.mib.asl.framework.api.displaymanagement.ASLDisplaymanagementFactory;
import de.vw.mib.asl.framework.api.displaymanagement.displayable.DisplayableService;
import de.vw.mib.asl.framework.api.displaymanagement.displayable.DisplayableServiceAdapter;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.DSIMapViewerControlFactoryVW;
import de.vw.mib.asl.internal.navigation.map.mainmap.mapswitch.MapViewerMapSwitchTargetHSM;
import de.vw.mib.genericevents.EventGeneric;
import de.vw.mib.genericevents.hsm.AbstractHsmState;
import de.vw.mib.genericevents.hsm.Hsm;
import de.vw.mib.genericevents.hsm.HsmState;

public class MapViewerMapSwitchStateInit
extends AbstractHsmState {
    private IExtLogger logger = ASLNavigationUtilFactory.getNavigationUtilApi().getExtLogger(65536, "[MapViewerMapSwitchStateInit]");
    private MapViewerMapSwitchTargetHSM target;
    private static final int[] ASL_OBSERVERS = new int[]{1074841939, 1074841976, 3400029, 1074841846, 1074841845, 3499072, 1073742385, 3499028, 3499029, 1073742416, 1073742406, 3499074};
    private static final int[] ASL_SERVICES = new int[]{3499072, 3499074};
    private static final int[] ATTRIBUTES_MAPVIEWER_CONTROL = new int[0];

    public MapViewerMapSwitchStateInit(MapViewerMapSwitchTargetHSM mapViewerMapSwitchTargetHSM, Hsm hsm, String string, HsmState hsmState) {
        super(hsm, string, hsmState);
        this.target = mapViewerMapSwitchTargetHSM;
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
            case 101001: {
                this.handleNaviTargetGoOn();
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
            this.logger.makeTrace().append("handleDefault(ev.Id=").append(eventGeneric.getReceiverEventId()).append(" Params: ").append(eventGeneric.getParamString()).append(")").log();
        }
    }

    private void handleEntry() {
        this.logger.trace("handleEntry()");
    }

    private void handleStart() throws Exception {
        this.logger.trace("handleStart()");
    }

    private void handleExit() {
        this.logger.trace("handleExit()");
    }

    private void handleNaviTargetGoOn() throws Exception {
        this.logger.trace("handleNaviTargetGoOn()");
        this.initDSI();
        this.initASL();
        this.initDisplayManagement();
        if (this.target.datapool.isMapLocatedInKombi()) {
            this.logger.trace("Last mode: Map was visible in Kombi - set switch state so a switch is triggered as soon as MOST is available");
            this.target.datapool.setMapSwitchState(5);
            this.target.notifierModel.notifyMainMapNotShownInABT();
            this.target.datapool.setMapVisibilityForFPKSwitch(false);
        } else {
            this.target.datapool.setMapSwitchState(1);
            this.target.datapool.setMapVisibilityForFPKSwitch(true);
            if (!this.target.datapool.isMapSwitchFunctionAvailableInKombi()) {
                this.target.notifierModel.notifyMapSwitchButtonDisabled();
            }
        }
        this.target.transStateWork();
    }

    private void initASL() {
        this.logger.trace("initASL()");
        this.initASLServices();
        this.initASLObservers();
    }

    private void initASLObservers() {
        this.logger.trace("initASLObservers()");
        this.target.addObservers(ASL_OBSERVERS);
    }

    private void initASLServices() {
        this.logger.trace("initASLServices()");
        this.target.registerServices(ASL_SERVICES, false);
    }

    private void initDSI() throws Exception {
        this.logger.trace("initDSI()");
        this.target.notifierDSI.setDsiMapViewerControl(DSIMapViewerControlFactoryVW.createMapViewerMain(this.target, ATTRIBUTES_MAPVIEWER_CONTROL));
    }

    private void initDisplayManagement() {
        DisplayableService displayableService = ASLDisplaymanagementFactory.getDisplaymanagementApi().getDisplayableService();
        DisplayableServiceAdapter displayableServiceAdapter = new DisplayableServiceAdapter(){

            public void onDisplayableShown(int n) {
                MapViewerMapSwitchStateInit.this.logger.makeTrace().append("onDisplayableShown(displayable = ").append(n).append(")").log();
                if (n == 3 && ((MapViewerMapSwitchStateInit)MapViewerMapSwitchStateInit.this).target.datapool.isMapFPKSwitchRunning()) {
                    MapViewerMapSwitchStateInit.this.logger.trace("Displayable Map is shown");
                    ((MapViewerMapSwitchStateInit)MapViewerMapSwitchStateInit.this).target.datapool.setMainMapLocatedInAbt(true);
                    ((MapViewerMapSwitchStateInit)MapViewerMapSwitchStateInit.this).target.datapool.setMapVisibilityForFPKSwitch(true);
                    ((MapViewerMapSwitchStateInit)MapViewerMapSwitchStateInit.this).target.notifierDSI.touchApproach(((MapViewerMapSwitchStateInit)MapViewerMapSwitchStateInit.this).target.datapool.isTouchApproximated());
                    ASLNavigationMapFactory.getNavigationMapApi().sendEvKombiMapDisplayableMapShown();
                }
            }

            public void onDisplayableHidden(int n) {
                MapViewerMapSwitchStateInit.this.logger.makeTrace().append("onDisplayableHidden(displayable = ").append(n).append(")").log();
                if (n == 3 && ((MapViewerMapSwitchStateInit)MapViewerMapSwitchStateInit.this).target.datapool.isMapFPKSwitchRunning()) {
                    MapViewerMapSwitchStateInit.this.logger.trace("Displayable Map is hidden");
                    ((MapViewerMapSwitchStateInit)MapViewerMapSwitchStateInit.this).target.datapool.setMainMapLocatedInAbt(false);
                    ((MapViewerMapSwitchStateInit)MapViewerMapSwitchStateInit.this).target.datapool.setMapVisibilityForFPKSwitch(false);
                    ((MapViewerMapSwitchStateInit)MapViewerMapSwitchStateInit.this).target.notifierDSI.touchApproach(false);
                    ASLNavigationMapFactory.getNavigationMapApi().sendEvKombiMapDisplayableMapHidden();
                }
            }
        };
        if (displayableService != null) {
            displayableService.addListener(displayableServiceAdapter);
        }
    }
}

