/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.asl.service;

import de.vw.mib.asl.api.navigation.util.ASLNavigationUtilFactory;
import de.vw.mib.asl.api.navigation.util.IExtLogger;
import de.vw.mib.asl.framework.internal.framework.AbstractASLHsmTarget;

public class ASLNavigationServiceMainMapNotifierModel {
    private final IExtLogger logger = ASLNavigationUtilFactory.getNavigationUtilApi().getExtLogger(65536, "[ASLNavigationServiceMainMapNotifierModel]");

    public void notifyMainMapNotShownInABT() {
        this.logger.trace("notifyMapNotShownInABT()");
        AbstractASLHsmTarget.writeBooleanToDatapool(1110166, false);
    }

    protected void notifyMainMapShownInABT() {
        this.logger.trace("notifyMapShownInABT()");
        AbstractASLHsmTarget.writeBooleanToDatapool(1110166, true);
    }

    public void notifyMapSwitchButtonDisabled() {
        this.logger.trace("notifyMapSwitchButtonDisabled()");
        AbstractASLHsmTarget.writeBooleanToDatapool(1110165, false);
    }

    public void notifyMapSwitchButtonEnabled() {
        this.logger.trace("notifyMapSwitchButtonEnabled()");
        AbstractASLHsmTarget.writeBooleanToDatapool(1110165, true);
    }

    public void notifyOverviewZoomOff() {
        this.logger.trace("notifyOverviewZoomOff()");
        AbstractASLHsmTarget.writeBooleanToDatapool(876, false);
    }
}

