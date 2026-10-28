/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.mainmap;

import de.vw.mib.asl.api.navigation.util.ASLNavigationUtilFactory;
import de.vw.mib.asl.api.navigation.util.IExtLogger;
import de.vw.mib.asl.internal.navigation.map.mainmap.AbstractMapViewerStateMapScaleContinuous;
import de.vw.mib.asl.internal.navigation.map.mainmap.MapViewerTargetHSM;
import de.vw.mib.genericevents.EventGeneric;
import de.vw.mib.genericevents.hsm.HsmState;

public class MapViewerStateMapScaleContinuousIn
extends AbstractMapViewerStateMapScaleContinuous {
    private static final int STEP_VALUE = -1;
    private final IExtLogger logger = ASLNavigationUtilFactory.getNavigationUtilApi().getExtLogger(65536, "[MapViewerKombiTargetHSM - MapViewerKombiStateMapScaleContinuousIn]");
    private EventGeneric event;

    public MapViewerStateMapScaleContinuousIn(MapViewerTargetHSM mapViewerTargetHSM, String string, HsmState hsmState) {
        super(mapViewerTargetHSM, string, hsmState);
    }

    protected void handleEntry() {
        super.handleEntry();
        this.logger.trace("handleEntry()");
        this.event = this.eventFactory.newEvent(this.target.getTargetId(), this.target.getTargetId(), 1073744564);
        this.event.setInt(0, -1);
    }

    protected void handleStart() {
        super.handleStart();
        this.logger.trace("handleStart()");
        this.timerServer.restartOrStartTimedEvent(this.event, 500L, true);
    }

    protected void handleExit() {
        super.handleExit();
        this.timerServer.stopTimedEvent(this.target.getTargetId(), 1073744564);
    }
}

