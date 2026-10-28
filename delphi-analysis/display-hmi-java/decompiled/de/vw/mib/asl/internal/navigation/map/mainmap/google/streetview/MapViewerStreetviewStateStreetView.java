/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.mainmap.google.streetview;

import de.vw.mib.asl.api.navigation.util.ASLNavigationUtilFactory;
import de.vw.mib.asl.api.navigation.util.IExtLogger;
import de.vw.mib.asl.internal.navigation.map.mainmap.google.streetview.MapViewerStreetviewTargetHSM;
import de.vw.mib.genericevents.EventGeneric;
import de.vw.mib.genericevents.GenericEventException;
import de.vw.mib.genericevents.hsm.AbstractHsmState;
import de.vw.mib.genericevents.hsm.Hsm;
import de.vw.mib.genericevents.hsm.HsmState;
import org.dsi.ifc.global.NavLocation;
import org.dsi.ifc.global.NavLocationWgs84;

public class MapViewerStreetviewStateStreetView
extends AbstractHsmState {
    private static final int[] ROTATION_STEPS = new int[]{0, 22, 45, 67, 90, 112, 135, 157, 180, 202, 225, 247, 270, 292, 315, 337};
    private final IExtLogger logger;
    private final MapViewerStreetviewTargetHSM target;
    private int xCurrent;
    private int yCurrent;
    private boolean zoomEnabled;

    public MapViewerStreetviewStateStreetView(MapViewerStreetviewTargetHSM mapViewerStreetviewTargetHSM, Hsm hsm, String string, HsmState hsmState) {
        super(hsm, string, hsmState);
        this.target = mapViewerStreetviewTargetHSM;
        this.logger = ASLNavigationUtilFactory.getNavigationUtilApi().getExtLogger(65536, "[MapViewerStreetviewStateStreetView]");
    }

    public HsmState dsiMapViewerStreetViewCtrlStreetViewEnabled(boolean bl) {
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("dsiMapViewerStreetViewCtrlStreetViewEnabled(").append(bl).append(")").log();
        }
        return null;
    }

    public void dsiMapViewerStreetViewCtrlUpdatePosition(NavLocationWgs84 navLocationWgs84, int n) {
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("dsiMapViewerStreetViewCtrlUpdatePosition(").append(navLocationWgs84.toString()).append(")").log();
        }
        this.updateDetailLine(navLocationWgs84);
    }

    public HsmState dsiMapViewerStreetViewCtrlUpdateRotation(int n, int n2, int n3) {
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("dsiMapViewerStreetViewCtrlUpdateRotation(phi=").append(n).append(", theta=").append(n2).append(")").log();
        }
        n /= 100;
        n += 180;
        n = 360 - n;
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("angle=").append(n).log();
        }
        int n4 = 0;
        for (int i = 0; i < ROTATION_STEPS.length - 1; ++i) {
            if (n < ROTATION_STEPS[i] || n >= ROTATION_STEPS[i + 1]) continue;
            n4 = ROTATION_STEPS[i + 1];
            break;
        }
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("calculated heading value is: ").append(n4).log();
        }
        this.target.notifierModel.notifyStreetViewHeadingValueChanged(n4);
        return null;
    }

    public HsmState dsiMapViewerStreetViewCtrlUpdateStreetViewLoadStatus(int n, int n2) {
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("dsiMapViewerStreetViewCtrlUpdateStreetViewLoadStatus(").append(n).append(")").log();
        }
        this.target.notifierModel.notifyStreetViewLoadStatus(n);
        if (n == 2) {
            this.target.notifierDSI.mapViewerGetInfoForScreenPosition(this.target, this.target.datapool.getHotPoint());
            this.zoomEnabled = true;
        }
        return null;
    }

    public void dsiNavigationLiGetLocationDescriptionTransformResult(NavLocation navLocation) {
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("dsiNavigationLiGetLocationDescriptionTransform(").append(navLocation.toString()).append(")").log();
        }
        this.target.notifierModel.notifyStreetViewLocationDataChanged(navLocation);
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
            case 0x40000AAA: {
                this.handleSetClickInStreetView(eventGeneric);
                break;
            }
            case 1073744488: {
                this.handleSetStreetViewVisible(eventGeneric);
                break;
            }
            case 1073744549: {
                this.handleZoomIn();
                break;
            }
            case 1073744550: {
                this.handleZoomOut();
                break;
            }
            case 1074841896: {
                this.handleTwoFingerZoom(eventGeneric);
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
            this.logger.makeTrace().append("handleDefault(").append(eventGeneric.toString()).append(")").log();
        }
    }

    private void handleEntry() {
        this.logger.trace("handleEntry()");
        NavLocationWgs84 navLocationWgs84 = this.target.datapool.getStreetViewPosition();
        this.updateDetailLine(navLocationWgs84);
        this.target.notifierDSI.mapViewerViewSetInvisible();
        int n = this.target.datapool.getZoomListIndexMax();
        float f = this.target.datapool.getZoomList()[n];
        this.target.datapool.setZoomListIndex(n);
        this.target.datapool.setZoomLevel(f);
        this.target.notifierDSI.streetViewLoadTrue();
        this.target.notifierDSI.streetViewSetZoomIndex(n);
        this.target.notifierDSI.streetViewSetCrosshairVisible();
        this.target.notifierDSI.streetViewSetVisible();
        this.target.notifierDSI.streetViewSetViewFreezeFalse();
        this.target.presetZoomLevelAndIndexStreetView();
    }

    private void handleExit() {
        this.logger.trace("handleExit()");
    }

    private void handleSetClickInStreetView(EventGeneric eventGeneric) throws GenericEventException {
        int n = eventGeneric.getInt(0);
        switch (n) {
            case 0: {
                this.handleSetClickInStreetViewPressed(eventGeneric);
                break;
            }
            case 1: {
                this.handleSetClickInStreetViewDragged(eventGeneric);
                break;
            }
            case 2: {
                this.handleSetClickInStreetViewReleased(eventGeneric);
                break;
            }
            case 3: {
                this.handleSetClickInStreetViewClicked();
                break;
            }
            case 4: {
                this.handleSetClickInStreetViewSelected(eventGeneric);
                break;
            }
        }
    }

    private void handleSetClickInStreetViewClicked() {
        this.logger.trace("handleSetClickInStreetViewClicked()");
        this.target.notifierDSI.streetViewGoToView();
    }

    private void handleSetClickInStreetViewDragged(EventGeneric eventGeneric) throws GenericEventException {
        this.logger.trace("handleSetClickInStreetViewDragged()");
        int n = eventGeneric.getInt(1);
        int n2 = eventGeneric.getInt(2);
        int n3 = n - this.xCurrent;
        int n4 = n2 - this.yCurrent;
        this.xCurrent = n;
        this.yCurrent = n2;
        if (n3 < Short.MIN_VALUE || n3 > Short.MAX_VALUE) {
            this.logger.makeWarn().append("the calculated value for xDiff is out of range, execution stopped");
            return;
        }
        if (n4 < Short.MIN_VALUE || n4 > Short.MAX_VALUE) {
            this.logger.makeWarn().append("the calculated value for yDiff is out of range, execution stopped");
            return;
        }
        this.target.notifierDSI.streetViewDragged((short)n3, (short)n4);
    }

    private void handleSetClickInStreetViewPressed(EventGeneric eventGeneric) throws GenericEventException {
        this.logger.trace("handleSetClickInStreetViewPressed()");
        this.xCurrent = eventGeneric.getInt(1);
        this.yCurrent = eventGeneric.getInt(2);
    }

    private void handleSetClickInStreetViewReleased(EventGeneric eventGeneric) throws GenericEventException {
        this.logger.trace("handleSetClickInStreetViewReleased()");
        this.xCurrent = eventGeneric.getInt(1);
        this.yCurrent = eventGeneric.getInt(2);
    }

    private void handleSetClickInStreetViewSelected(EventGeneric eventGeneric) throws GenericEventException {
        this.logger.trace("handleSetClickInStreetViewSelected()");
        this.xCurrent = eventGeneric.getInt(1);
        this.yCurrent = eventGeneric.getInt(2);
    }

    private void handleSetStreetViewVisible(EventGeneric eventGeneric) throws Exception {
        boolean bl = eventGeneric.getBoolean(0);
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("handleSetStreetViewVisible( visible=").append(bl).append(" )").log();
        }
        if (!bl) {
            this.target.transStateStreetViewInvisible();
        } else {
            this.logger.warn("StreetView is already enabled");
        }
    }

    private void handleStart() {
        this.logger.trace("handleStart()");
    }

    private void handleTwoFingerZoom(EventGeneric eventGeneric) throws Exception {
        int n = eventGeneric.getInt(0);
        int n2 = eventGeneric.getInt(1);
        int n3 = eventGeneric.getInt(2);
        int n4 = eventGeneric.getInt(3);
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("handleTwoFingerZoom(x= ").append(n).append(", y=").append(n2).append(", zDeltaX=").append(n3).append(", zDeltaY=").append(n4).append(")").log();
        }
        this.target.datapool.setTwoFingerZDistance(n4);
        this.target.transStateStreetViewTwoFingerZoom();
    }

    private void handleZoomIn() {
        this.logger.trace("handleZoomIn()");
        if (!this.zoomEnabled) {
            return;
        }
        this.target.streetViewZoomIn();
    }

    private void handleZoomOut() throws Exception {
        this.logger.trace("handleZoomOut()");
        if (!this.zoomEnabled) {
            return;
        }
        this.target.streetViewZoomOut();
    }

    private void updateDetailLine(NavLocationWgs84 navLocationWgs84) {
        if (navLocationWgs84 == null) {
            return;
        }
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("updateDetailLine(").append(navLocationWgs84.toString()).append(")").log();
        }
        NavLocation navLocation = ASLNavigationUtilFactory.getNavigationUtilApi().getLocationWrapper(navLocationWgs84.latitude, navLocationWgs84.longitude).getLocation();
        this.target.notifierDSI.navigationLiGetLocationDescriptionTransform(navLocation);
    }
}

