/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.androidauto.target;

import de.vw.mib.asl.framework.internal.framework.ServiceManager;
import de.vw.mib.asl.internal.androidauto.target.AndroidAutoTarget;
import de.vw.mib.popup.PopupInformationHandler;

public class PopupHandler
implements PopupInformationHandler {
    private AndroidAutoTarget target;

    public PopupHandler(AndroidAutoTarget androidAutoTarget) {
        this.target = androidAutoTarget;
    }

    public void onPopupInformationChanged(int n) {
        if (this.target.isTraceEnabled()) {
            this.target.trace("PopupHandler::onPopupInformationChanged - popupInfo = " + n);
        }
        ServiceManager.aslPropertyManager.valueChangedBoolean(2910003, n == 2);
    }
}

