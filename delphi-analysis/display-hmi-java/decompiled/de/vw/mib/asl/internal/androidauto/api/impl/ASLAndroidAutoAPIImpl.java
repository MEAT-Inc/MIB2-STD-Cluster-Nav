/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.androidauto.api.impl;

import de.vw.mib.asl.api.androidauto.ASLAndroidAutoAPI;
import de.vw.mib.asl.api.androidauto.ASLAndroidAutoExBoxService;
import de.vw.mib.asl.framework.internal.framework.id.PreRegisteredIds;
import de.vw.mib.asl.internal.androidauto.api.impl.ASLAndroidAutoExBoxServiceImpl;

public class ASLAndroidAutoAPIImpl
implements ASLAndroidAutoAPI {
    ASLAndroidAutoExBoxService service;

    public ASLAndroidAutoExBoxService getExBoxService() {
        if (this.service == null) {
            this.service = new ASLAndroidAutoExBoxServiceImpl();
        }
        return this.service;
    }

    static {
        PreRegisteredIds.addServiceOrObserverToArray(2, 1590002, 1076641824);
        PreRegisteredIds.addServiceOrObserverToArray(2, 1590002, 1076641825);
        PreRegisteredIds.addServiceOrObserverToArray(2, 1590002, 1076641826);
        PreRegisteredIds.addServiceOrObserverToArray(2, 1590002, 1076641828);
        PreRegisteredIds.addServiceOrObserverToArray(0, 1590002, 6200002);
        PreRegisteredIds.addServiceOrObserverToArray(0, 1590002, 6200003);
    }
}

