/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.setup.google.earth;

import de.vw.mib.asl.api.navigation.util.ASLNavigationUtilFactory;
import de.vw.mib.asl.api.navigation.util.IExtLogger;
import de.vw.mib.asl.framework.internal.framework.AbstractASLHsmTarget;
import org.dsi.ifc.global.ResourceLocator;

public class GoogleEarthSetupNotifierModel {
    private final IExtLogger logger = ASLNavigationUtilFactory.getNavigationUtilApi().getExtLogger(65536, "[GoogleEarthSetupNotifierModel]");

    public void notifyGoogleEarthDataStatusChanged(int n) {
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("notifyGoogleEarthDataStatusChanged(googleDataStatus=").append(n).append(")").log();
        }
        AbstractASLHsmTarget.writeIntegerToDatapool(4013, n);
    }

    public void setLayerAvailable() {
        this.logger.trace("setLayerAvailable()");
        AbstractASLHsmTarget.writeBooleanToDatapool(1110152, true);
    }

    public void setLayerBusinessAvailable() {
        this.logger.trace("setLayerBusinessAvailable()");
        AbstractASLHsmTarget.writeBooleanToDatapool(1110061, true);
    }

    public void setLayerBusinessIcon(ResourceLocator resourceLocator) {
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("setIconLayerBusiness(resLocator=").append(resourceLocator.toString()).append(")").log();
        }
        AbstractASLHsmTarget.writeResourceLocatorToDatapool(1110022, resourceLocator);
    }

    public void setLayerBusinessInvisible() {
        this.logger.trace("setLayerBusinessInvisible()");
        AbstractASLHsmTarget.writeBooleanToDatapool(0x10F001, false);
    }

    public void setLayerBusinessVisible() {
        this.logger.trace("setLayerBusinessVisible()");
        AbstractASLHsmTarget.writeBooleanToDatapool(0x10F001, true);
    }

    public void setLayerPanoramioAvailable() {
        this.logger.trace("setLayerPanoramioAvailable()");
        AbstractASLHsmTarget.writeBooleanToDatapool(1110062, true);
    }

    public void setLayerPanoramioIcon(ResourceLocator resourceLocator) {
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("setIconLayerPanoramio(resLocator=").append(resourceLocator.toString()).append(")").log();
        }
        AbstractASLHsmTarget.writeResourceLocatorToDatapool(1110023, resourceLocator);
    }

    public void setLayerPanoramioInvisible() {
        this.logger.trace("setLayerPanoramioInvisible()");
        AbstractASLHsmTarget.writeBooleanToDatapool(1110018, false);
    }

    public void setLayerPanoramioVisible() {
        this.logger.trace("setLayerPanoramioVisible()");
        AbstractASLHsmTarget.writeBooleanToDatapool(1110018, true);
    }

    public void setLayerPlacesAvailable() {
        this.logger.trace("setLayerPlacesAvailable()");
        AbstractASLHsmTarget.writeBooleanToDatapool(1110063, true);
    }

    public void setLayerPlacesIcon(ResourceLocator resourceLocator) {
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("setIconLayerPlaces(resLocator=").append(resourceLocator.toString()).append(")").log();
        }
        AbstractASLHsmTarget.writeResourceLocatorToDatapool(1110021, resourceLocator);
    }

    public void setLayerPlacesInvisible() {
        this.logger.trace("setLayerPlacesInvsible()");
        AbstractASLHsmTarget.writeBooleanToDatapool(0x10F000, false);
    }

    public void setLayerPlacesVisible() {
        this.logger.trace("setLayerPlacesVisible()");
        AbstractASLHsmTarget.writeBooleanToDatapool(0x10F000, true);
    }

    public void setLayerWikipediaAvailable() {
        this.logger.trace("setLayerWikipediaAvailable()");
        AbstractASLHsmTarget.writeBooleanToDatapool(1110064, true);
    }

    public void setLayerWikipediaIcon(ResourceLocator resourceLocator) {
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("setIconLayerWikipedia(resLocator=").append(resourceLocator.toString()).append(")").log();
        }
        AbstractASLHsmTarget.writeResourceLocatorToDatapool(1110024, resourceLocator);
    }

    public void setLayerWikipediaInvisible() {
        this.logger.trace("setLayerWikipediaInvisible()");
        AbstractASLHsmTarget.writeBooleanToDatapool(1110019, false);
    }

    public void setLayerWikipediaVisible() {
        this.logger.trace("setLayerWikipediaVisible()");
        AbstractASLHsmTarget.writeBooleanToDatapool(1110019, true);
    }
}

