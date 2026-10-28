/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.dsi;

import de.vw.mib.genericevents.AbstractTarget;
import org.dsi.ifc.global.NavLocation;
import org.dsi.ifc.global.NavLocationWgs84;
import org.dsi.ifc.global.NavRectangle;
import org.dsi.ifc.map.MapFlag;
import org.dsi.ifc.map.Point;
import org.dsi.ifc.map.Rect;

public interface DSIMapViewerControlVW {
    public void configureFlags(int var1, MapFlag[] var2);

    public void dragMap(short var1, short var2);

    public void dragRoute(short var1, short var2);

    public void ehSetCategoryVisibility(int[] var1, boolean[] var2);

    public void ehSetCategoryVisibilityToDefault();

    public void ensurePoiVisibility(NavLocation[] var1);

    public void ensureTMCVisibility(long var1);

    public void getInfoForScreenPosition(AbstractTarget var1, Point var2);

    public void goToTMCMessage(long var1);

    public void rbSelectAlternativeRoute(int var1);

    public void set3DLandmarksVisible(boolean var1);

    public void setBrandIconStyle(int[] var1, int var2);

    public void setCarPosition(Point var1);

    public void setCityModelMode(int var1);

    public void setDayView();

    public void setDragRouteMarker(int var1);

    public void setEnableSoftJump(boolean var1);

    public void setEnableSoftTilt(boolean var1);

    public void setEnableSoftZoom(boolean var1);

    public void setGeneralPoiVisibility(boolean var1);

    public void setHotPoint(Point var1);

    public void setLocation(int var1, short var2);

    public void setLocationByLocation(NavLocation var1);

    public void setMapLayerVisible(int[] var1);

    public void setMapViewPortByLD(NavLocation var1, NavLocation var2, int var3);

    public void setMapViewPortByWGS84Rectangle(NavRectangle var1, int var2);

    public void setMetricSystem(int var1);

    public void setMobilityHorizonVisibility(boolean var1);

    public void setMobilityHorizonZoomMode(int var1);

    public void setMode(int var1);

    public void setNightView();

    public void setOrientation(int var1, Point var2);

    public void setRotation(short var1);

    public void setRouteColoringPolicy(int var1);

    public void setRouteVisibility(boolean var1);

    public void setScreenViewport(Rect var1);

    public void setScreenViewportMaximum(Rect var1);

    public void setSpeedAndFlowRoadClass(int var1);

    public void setTemperatureScale(int var1);

    public void setTrafficMapStyle(boolean var1);

    public void setViewType(int var1);

    public void setZoomArea(Rect var1);

    public void setZoomLevel(float var1, int var2);

    public void showSpeedAndFlowCongestions(boolean var1);

    public void showSpeedAndFlowFreeFlow(boolean var1);

    public void showTMCMessages(boolean var1);

    public void showTrafficEventListView(long[] var1, boolean var2, boolean var3);

    public void startRouteDragging(NavLocationWgs84 var1);

    public void stopScrollToDirection();

    public void touchApproach(boolean var1);

    public void viewFreeze(boolean var1);

    public void viewSetVisible(boolean var1);
}

