/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.dsi;

import org.dsi.ifc.map.Point;
import org.dsi.ifc.map.Rect;

public interface DSIMapViewerZoomEngineVW {
    public void autoZoomEnable(boolean var1);

    public void setCarPosition(Point var1);

    public void setMapOrientation(int var1);

    public void setMapRotation(short var1);

    public void setViewType(int var1);

    public void setZoomArea(Rect var1);
}

