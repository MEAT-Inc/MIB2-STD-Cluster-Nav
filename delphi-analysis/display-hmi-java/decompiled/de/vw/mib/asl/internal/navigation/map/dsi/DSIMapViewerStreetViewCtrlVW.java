/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.dsi;

import org.dsi.ifc.global.NavLocationWgs84;
import org.dsi.ifc.map.Rect;

public interface DSIMapViewerStreetViewCtrlVW {
    public void goToView();

    public void loadStreetView(boolean var1);

    public void rotateView(short var1, short var2);

    public void setCrossHairsVisibility(boolean var1);

    public void setDayNightView(boolean var1);

    public void setPosition(NavLocationWgs84 var1);

    public void setScreenViewport(Rect var1);

    public void setStreetViewZoomIndex(int var1);

    public void setStreetViewZoomLevel(float var1);

    public void streetViewEnabled(boolean var1);

    public void streetViewFreeze(boolean var1);

    public void streetViewVisible(boolean var1);
}

