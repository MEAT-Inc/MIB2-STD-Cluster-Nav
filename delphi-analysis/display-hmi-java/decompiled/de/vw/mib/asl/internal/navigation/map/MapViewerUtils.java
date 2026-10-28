/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map;

import de.vw.mib.asl.api.navigation.util.ASLNavigationUtilFactory;
import de.vw.mib.asl.api.navigation.util.IExtLogger;
import de.vw.mib.asl.internal.navigation.map.dsi.datapool.MapDataPool;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.DSIMapViewerControlFactoryVW;
import de.vw.mib.asl.internal.navigation.map.mainmap.MapViewerDatapoolShared;
import de.vw.mib.asl.internal.navigation.map.setup.PersistedMapSetup;
import org.dsi.ifc.global.NavLocation;
import org.dsi.ifc.map.Point;
import org.dsi.ifc.map.Rect;

public final class MapViewerUtils {
    public static final int HOME_ID = 200;
    private static final int ZOOM_LEVEL_MINIMUM = 3000;
    private static final double HEADING_OUTPUT_RANGE = 3.6;
    private static final double HEADING_OUTPUT_UNIT = 22.5;
    private static IExtLogger LOGGER = null;

    public static int calculateHeadingValue(short s) {
        s = (short)(360 - s);
        int n = (int)((double)s / 22.5);
        double d = (double)s % 22.5;
        int n2 = d > 11.25 ? (int)(22.5 * (double)(n + 1)) : (int)(22.5 * (double)n);
        return n2;
    }

    public static Point calculateHotPointByZoomArea(Rect rect) {
        return new Point(rect.kordX + rect.diffX / 2, rect.kordY + rect.diffY / 2);
    }

    public static int calculateZoomLevelNormalized(float f) {
        if (MapViewerUtils.getLogger().isTraceEnabled()) {
            MapViewerUtils.getLogger().makeTrace().append("calculateNormalizedZoomLevel( zoomLevel=").append(f).append(" )").log();
        }
        int n = MapViewerUtils.calculateZoomIndexByZoomLevel(f);
        int n2 = (int)MapViewerUtils.calculateZoomLevelByZoomIndex(n) / 100;
        if (MapViewerUtils.getLogger().isTraceEnabled()) {
            MapViewerUtils.getLogger().makeTrace().append("zoomLevelNormalized=").append(n2).append(" )").log();
        }
        return n2;
    }

    public static int calculateZoomIndexByZoomLevel(float f) {
        MapDataPool mapDataPool = DSIMapViewerControlFactoryVW.getMapDatapoolMain();
        float[] fArray = mapDataPool.getZoomList();
        int n = fArray.length - 1;
        if (fArray == null || fArray.length == 0) {
            MapViewerUtils.getLogger().error("Invalid zoomList, using zoomListIndex 0");
            return 0;
        }
        if (MapViewerUtils.getLogger().isTraceEnabled()) {
            MapViewerUtils.getLogger().makeTrace().append("calculateZoomIndexByZoomLevel(zoomLevel=").append(f).append(",zoomListLastIndex=").append(n).append(")").log();
        }
        if (f < fArray[0] || f > fArray[n]) {
            MapViewerUtils.getLogger().makeError().append("zoomLevel '").append(f).append("' is out of range, the zoomLevel will not be changed").log();
            return mapDataPool.getZoomListIndex();
        }
        for (int i = 0; i < fArray.length; ++i) {
            if (i == n) {
                return i;
            }
            float f2 = fArray[i + 1];
            float f3 = fArray[i];
            if (!(f < (f2 + f3) / 2.0f)) continue;
            if (MapViewerUtils.getLogger().isTraceEnabled()) {
                MapViewerUtils.getLogger().makeTrace().append("The zoomListIndex '").append(i).append("' was found for zoomLevel '").append(f).append("'.").log();
            }
            return i;
        }
        MapViewerUtils.getLogger().makeError().append("zoomLevel '").append(f).append("' not found in zoomList, using zoomListIndex 0").log();
        return 0;
    }

    public static float calculateZoomLevelByZoomIndex(int n) {
        MapDataPool mapDataPool = DSIMapViewerControlFactoryVW.getMapDatapoolMain();
        float[] fArray = mapDataPool.getZoomList();
        if (fArray == null || fArray.length == 0) {
            MapViewerUtils.getLogger().makeError().append("The zoomList is null, we can't calculate the zoomLevel for zoomListIndex '").append(n).append("'").log();
            return 3000.0f;
        }
        if (n < 0 || n >= fArray.length) {
            MapViewerUtils.getLogger().makeError().append("The zoomListIndex '").append(n).append("' is out of range (0 - ").append(fArray.length).append("), we can't calculate a zoomLevel for this index").log();
            return 3000.0f;
        }
        if (MapViewerUtils.getLogger().isTraceEnabled()) {
            MapViewerUtils.getLogger().makeTrace().append("calculateZoomLevelByZoomIndex( zoomListIndex=").append(n).append(" ) - zoomLevel=").append(fArray[n]).log();
        }
        return fArray[n];
    }

    public static int calculateZoomListIndexNew(int n) {
        MapDataPool mapDataPool = DSIMapViewerControlFactoryVW.getMapDatapoolMain();
        return MapViewerUtils.calculateZoomListFromDatapool(n, mapDataPool);
    }

    public static int calculateZoomListIndexForKombiNew(int n) {
        MapDataPool mapDataPool = DSIMapViewerControlFactoryVW.getMapDatapoolKombi();
        return MapViewerUtils.calculateZoomListFromDatapool(n, mapDataPool);
    }

    static int calculateZoomListFromDatapool(int n, MapDataPool mapDataPool) {
        int n2;
        int n3 = mapDataPool.getZoomListIndex();
        if (n3 == -1) {
            n3 = MapViewerUtils.calculateZoomIndexByZoomLevel(mapDataPool.getZoomLevel());
        }
        if ((n2 = n3 + n) < mapDataPool.getZoomListIndexMin()) {
            n2 = mapDataPool.getZoomListIndexMin();
        } else if (n2 > mapDataPool.getZoomListIndexMax()) {
            n2 = mapDataPool.getZoomListIndexMax();
        }
        return n2;
    }

    public static float checkZoomLevelIsInRange(float f) {
        if (MapViewerUtils.getLogger().isTraceEnabled()) {
            MapViewerUtils.getLogger().makeTrace().append("checkZoomLevelIsInRange(zoomLevel=").append(f).append(")").log();
        }
        float[] fArray = DSIMapViewerControlFactoryVW.getMapDatapoolMain().getZoomList();
        boolean bl = false;
        int n = fArray.length - 1;
        if (f < fArray[0]) {
            MapViewerUtils.getLogger().makeWarn().append("zoomLevel '").append(f).append("' is out of range, using zoomListIndex 0").log();
            f = (int)fArray[0];
        } else if (f > fArray[n]) {
            MapViewerUtils.getLogger().makeWarn().append("zoomLevel '").append(f).append("' is out of range, using zoomListIndex ").append(n).log();
            f = (int)fArray[n];
        }
        return f;
    }

    public static boolean isMainMapMaximumZoomListIndexFor3DReached() {
        PersistedMapSetup persistedMapSetup = PersistedMapSetup.getInstance();
        float f = persistedMapSetup.getMainMapZoomLevel();
        return f > 1000000.0f;
    }

    public static boolean isMainMapMaximumZoomListIndexReached() {
        int n;
        MapDataPool mapDataPool = DSIMapViewerControlFactoryVW.getMapDatapoolMain();
        int n2 = mapDataPool.getZoomListIndex();
        return n2 >= (n = mapDataPool.getZoomListIndexMax());
    }

    public static boolean isMainMapModeCurrentDraggable() {
        int n = DSIMapViewerControlFactoryVW.getMapDatapoolMain().getMapMode();
        return MapViewerUtils.isMapModeDraggable(n);
    }

    public static boolean isMainMapModeCurrentZoomable() {
        int n = DSIMapViewerControlFactoryVW.getMapDatapoolMain().getMapMode();
        return MapViewerUtils.isMapModeZoomable(n);
    }

    public static boolean isMapInMapModeCurrentZoomable() {
        int n = DSIMapViewerControlFactoryVW.getMapDatapoolSplitScreen().getMapMode();
        return MapViewerUtils.isMapModeZoomable(n);
    }

    public static boolean isMapModeCurrentDraggable() {
        int n = DSIMapViewerControlFactoryVW.getMapDatapoolMain().getMapMode();
        return MapViewerUtils.isMapModeDraggable(n);
    }

    public static boolean isMapModeDraggable(int n) {
        if (n == 3) {
            return true;
        }
        return n == 2;
    }

    public static boolean isMapModeZoomable(int n) {
        if (n == 3) {
            return true;
        }
        if (n == 2) {
            return true;
        }
        if (n == 4) {
            return true;
        }
        if (n == 1) {
            return true;
        }
        return n == 9;
    }

    public static boolean isPositionValid(int n, int n2) {
        return n != 0 || n2 != 0;
    }

    public static boolean isPositionValid(NavLocation navLocation) {
        if (navLocation == null) {
            return false;
        }
        return MapViewerUtils.isPositionValid(navLocation.latitude, navLocation.longitude);
    }

    public static void updateMainMapPersistedZoomLevel(float f) {
        if (MapViewerUtils.istValidPerspectiveForUpdateMainMapPersistedZoomLevel()) {
            PersistedMapSetup.getInstance().setMainMapZoomLevel((int)f);
        } else if (MapViewerUtils.getLogger().isTraceEnabled()) {
            MapViewerUtils.getLogger().makeWarn().append("updateMainMapPersistedZoomLevel(zoomLevel=").append(f).append(") - the zoomLevel won't be persisted because we are not in a 2D or 3D perspective").log();
        }
    }

    private static boolean istValidPerspectiveForUpdateMainMapPersistedZoomLevel() {
        MapViewerDatapoolShared mapViewerDatapoolShared = MapViewerDatapoolShared.getInstance();
        if (mapViewerDatapoolShared.isPerspective25DCarUp()) {
            return true;
        }
        if (mapViewerDatapoolShared.isPerspective2DCarUp()) {
            return true;
        }
        if (mapViewerDatapoolShared.isPerspective2DNorthUp()) {
            return true;
        }
        if (mapViewerDatapoolShared.isPerspective3DCarUp()) {
            return true;
        }
        if (mapViewerDatapoolShared.isPerspective3DDTM()) {
            return true;
        }
        if (mapViewerDatapoolShared.isPerspectiveCountryOverview()) {
            return true;
        }
        if (mapViewerDatapoolShared.isPerspectiveDestinationZoom()) {
            return true;
        }
        if (mapViewerDatapoolShared.isPerspectiveFinalDestinationZoom()) {
            return true;
        }
        return mapViewerDatapoolShared.isPerspectiveOverviewZoom();
    }

    public static boolean isZoomLevelWithinRange(float f) {
        if (MapViewerUtils.getLogger().isTraceEnabled()) {
            MapViewerUtils.getLogger().makeTrace().append("isZoomLevelWithinRange(zoomLevel=").append(f).append(")").log();
        }
        float[] fArray = DSIMapViewerControlFactoryVW.getMapDatapoolMain().getZoomList();
        boolean bl = false;
        int n = fArray.length - 1;
        if (f < fArray[0]) {
            MapViewerUtils.getLogger().trace("zoomLevel is smaller than smallest level in list");
            return false;
        }
        if (f > fArray[n]) {
            MapViewerUtils.getLogger().trace("zoomLevel is larger than highest zoom level in list");
            return false;
        }
        return true;
    }

    private MapViewerUtils() {
    }

    private static IExtLogger getLogger() {
        if (LOGGER == null) {
            LOGGER = ASLNavigationUtilFactory.getNavigationUtilApi().getExtLogger(65536, "[MapViewerUtils]");
        }
        return LOGGER;
    }
}

