/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.mainmap.touchgestures;

import de.vw.mib.asl.api.navigation.util.ASLNavigationUtilFactory;
import de.vw.mib.asl.api.navigation.util.IExtLogger;
import de.vw.mib.asl.internal.navigation.map.dsi.DSIMapViewerControlVW;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.DSIMapViewerControlFactoryVW;
import de.vw.mib.asl.internal.navigation.map.mainmap.touchgestures.MapViewerTouchgesturesTargetHSM;
import de.vw.mib.genericevents.EventGeneric;
import de.vw.mib.genericevents.hsm.AbstractHsmState;
import de.vw.mib.genericevents.hsm.Hsm;
import de.vw.mib.genericevents.hsm.HsmState;

public final class MapViewerTouchgesturesStateInit
extends AbstractHsmState {
    private static final int[] ASL_OBSERVERS = new int[]{1073742411, 1074841824, 1074841825, 1073744379, 1073744199, 1074841840, 1074841876, 1074841837, 1074841932, 1074841933, 3499062};
    private final IExtLogger logger = ASLNavigationUtilFactory.getNavigationUtilApi().getExtLogger(65536, "[MapViewerTouchgesturesStateInit]");
    private final MapViewerTouchgesturesTargetHSM target;

    public MapViewerTouchgesturesStateInit(MapViewerTouchgesturesTargetHSM mapViewerTouchgesturesTargetHSM, Hsm hsm, String string, HsmState hsmState) {
        super(hsm, string, hsmState);
        this.target = mapViewerTouchgesturesTargetHSM;
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
        this.initDSI();
        this.initASL();
        this.target.transStateMain();
    }

    private void initASL() {
        this.logger.trace("initASL()");
        this.initASLAddObservers();
    }

    private void initASLAddObservers() {
        this.logger.trace("initASLAddObservers()");
        this.target.addObservers(ASL_OBSERVERS);
    }

    private void initDSI() throws Exception {
        this.logger.trace("initDSI()");
        DSIMapViewerControlVW dSIMapViewerControlVW = DSIMapViewerControlFactoryVW.createMapViewerMain(this.target, null);
        this.target.notifierDSI.setDsiMapViewerControl(dSIMapViewerControlVW);
    }
}

