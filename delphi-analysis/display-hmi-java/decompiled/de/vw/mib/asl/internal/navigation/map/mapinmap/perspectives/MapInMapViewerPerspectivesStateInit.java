/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.mapinmap.perspectives;

import de.vw.mib.asl.api.navigation.util.ASLNavigationUtilFactory;
import de.vw.mib.asl.api.navigation.util.IExtLogger;
import de.vw.mib.asl.internal.navigation.map.dsi.DSIMapViewerControlVW;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.DSIMapViewerControlFactoryVW;
import de.vw.mib.asl.internal.navigation.map.mapinmap.perspectives.MapInMapViewerPerspectivesTargetHsm;
import de.vw.mib.genericevents.EventGeneric;
import de.vw.mib.genericevents.hsm.AbstractHsmState;
import de.vw.mib.genericevents.hsm.HsmState;

public class MapInMapViewerPerspectivesStateInit
extends AbstractHsmState {
    public static final int[] ATTRIBUTES_MAPVIEWERCONTROL = new int[]{8};
    private static final int[] OBSERVERS = new int[]{1073742393, 1073742394, 1073742398, 0x40000242, 1073744395, 1073742403};
    private final IExtLogger logger = ASLNavigationUtilFactory.getNavigationUtilApi().getExtLogger(65536, "[MapInMapViewerPerspectivesStateInit]");
    private final MapInMapViewerPerspectivesTargetHsm target;

    public MapInMapViewerPerspectivesStateInit(MapInMapViewerPerspectivesTargetHsm mapInMapViewerPerspectivesTargetHsm, String string, HsmState hsmState) {
        super(mapInMapViewerPerspectivesTargetHsm.getHsm(), string, hsmState);
        this.target = mapInMapViewerPerspectivesTargetHsm;
    }

    public void dsiMapViewerControlUpdateViewFreeze(boolean bl, int n) throws Exception {
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("dsiMapViewerControlUpdateViewFreeze(viewFreeze=").append(bl).append(")").log();
        }
        if (!bl) {
            if (this.target.datapool.isPerspectiveOverviewZoomActive() && ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getRGIsActive()) {
                this.target.transStateOverviewZoom();
                return;
            }
            int n2 = this.target.datapool.getMapInMapPerspective();
            switch (n2) {
                case 0: {
                    this.target.transState2DNorthUp();
                    break;
                }
                case 1: {
                    this.target.transState2DCarUp();
                    break;
                }
                case 2: {
                    this.target.transState3DCarUp();
                    break;
                }
                default: {
                    this.target.transState2DCarUp();
                }
            }
        }
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
            case 101003: {
                this.handleNaviTargetPrepareOn(eventGeneric);
                break;
            }
            case 4: {
                this.handleExit();
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
            this.logger.makeTrace().append("handleDefault() ev.Id=").append(eventGeneric.getReceiverEventId()).append(" Params: ").append(eventGeneric.getParamString()).log();
        }
    }

    private void handleEntry() {
        this.logger.trace("handleEntry()");
    }

    private void handleExit() {
        this.logger.trace("handleExit()");
    }

    private void handleNaviTargetPrepareOn(EventGeneric eventGeneric) throws Exception {
        this.logger.trace("handleNaviTargetPrepareOn()");
        this.target.addObservers(OBSERVERS);
        this.initDSI();
    }

    private void handleStart() throws Exception {
        this.logger.trace("handleStart()");
    }

    private void initDSI() {
        this.logger.trace("initDSI()");
        this.initDSIMapViewer();
        this.initDSIMapViewerConfigurePersistedValues();
    }

    private void initDSIMapViewer() {
        this.logger.trace("initDSIMapViewer()");
        DSIMapViewerControlVW dSIMapViewerControlVW = DSIMapViewerControlFactoryVW.createMapViewerSplitscreen(this.target, ATTRIBUTES_MAPVIEWERCONTROL);
        this.target.notifierDSI.setDsiMapViewerControl(dSIMapViewerControlVW);
    }

    private void initDSIMapViewerConfigurePersistedValues() {
        this.logger.trace("initDSIMapViewerConfigurePersistedValues");
        this.target.notifierDSI.viewFreezeTrue();
        this.target.notifierDSI.setCityModelModeOff();
        this.target.notifierDSI.set3DLandmarksVisible();
        this.target.notifierDSI.setGeneralPoiVisibilityFalse();
        this.target.notifierDSI.viewSetInvisible();
        this.target.notifierDSI.viewFreezeFalse();
    }
}

