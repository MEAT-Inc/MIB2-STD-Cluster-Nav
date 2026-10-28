/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.mainmap.rocketzoom;

import de.vw.mib.asl.api.navigation.util.ASLNavigationUtilFactory;
import de.vw.mib.asl.api.navigation.util.IExtLogger;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.DSIMapViewerControlFactoryVW;
import de.vw.mib.asl.internal.navigation.map.mainmap.rocketzoom.MapViewerRocketzoomTargetHSM;
import de.vw.mib.genericevents.EventGeneric;
import de.vw.mib.genericevents.hsm.AbstractHsmState;
import de.vw.mib.genericevents.hsm.HsmState;

public class MapViewerRocketzoomStateInit
extends AbstractHsmState {
    private static final int[] ASL_OBSERVERS = new int[]{1073742385, 1073742408, 1073742406, 1074841920, 1073744396, 1073742416, 1073742418, 1073742389, 3499028, 3499029, 1074841824, 1074841825, 1073742420, 1073742422, 1073742411, 1073742382};
    private static final int[] ATTRIBUTES_MAPVIEWER = new int[]{11};
    private final IExtLogger logger = ASLNavigationUtilFactory.getNavigationUtilApi().getExtLogger(65536, "[MapViewerRocketzoomStateInit]");
    private final MapViewerRocketzoomTargetHSM target;

    public MapViewerRocketzoomStateInit(MapViewerRocketzoomTargetHSM mapViewerRocketzoomTargetHSM, String string, HsmState hsmState) {
        super(mapViewerRocketzoomTargetHSM.getHsm(), string, hsmState);
        this.target = mapViewerRocketzoomTargetHSM;
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
            default: {
                this.handleDefault(eventGeneric);
                return this.myParent;
            }
        }
        return null;
    }

    private void handleDefault(EventGeneric eventGeneric) {
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("handleDefault(): ev.Id=").append(eventGeneric.getReceiverEventId()).append(" Params: ").append(eventGeneric.getParamString()).log();
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
        this.initASL();
        this.initDSI();
        this.target.transStateInactive();
    }

    private void initASL() {
        this.logger.trace("initASL()");
        this.target.addObservers(ASL_OBSERVERS);
    }

    private void initDSI() {
        this.logger.trace("initDSI()");
        this.target.notifierDSI.setDsiMapViewerControl(DSIMapViewerControlFactoryVW.createMapViewerMain(this.target, ATTRIBUTES_MAPVIEWER));
    }
}

