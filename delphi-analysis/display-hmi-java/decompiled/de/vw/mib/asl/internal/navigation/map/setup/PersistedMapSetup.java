/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.setup;

import de.vw.mib.asl.api.navigation.util.ASLNavigationUtilFactory;
import de.vw.mib.asl.api.navigation.util.IPersistenceDefaults;
import de.vw.mib.asl.api.navigation.util.PersistableMap;
import de.vw.mib.asl.api.navigation.util.ReloadPersistedDataListener;
import de.vw.mib.asl.framework.internal.framework.ServiceManager;
import de.vw.mib.asl.internal.navigation.map.MapViewerUtils;
import org.dsi.ifc.map.Point;
import org.dsi.ifc.map.Rect;

public class PersistedMapSetup
implements ReloadPersistedDataListener {
    private static final String AUTOZOOM_MAIN_MAP = "mainmap";
    private static final int AUTOZOOM_MAIN_MAP_DEFAULT = 1;
    private static final String AUTOZOOM_MAP_IN_MAP = "mapinmap";
    private static final boolean AUTOZOOM_MAP_IN_MAP_DEFAULT = true;
    private static final String AUTOZOOM_RECOMMENDED_ZOOM_LAST = "recommendedzoom.last";
    private static final int AUTOZOOM_RECOMMENDED_ZOOM_LAST_DEFAULT = 10000;
    private static final String DUALSCREEN_VISIBILITIES = "dualscreen.visibilities";
    private static final int[] DUALSCREEN_VISIBILITIES_DEFAULT = new int[14];
    public static final int GOOGLE_EARTH_LAYER_BUSINESS = 1;
    public static final int GOOGLE_EARTH_LAYER_PANORAMIO = 2;
    public static final int GOOGLE_EARTH_LAYER_PLACES = 0;
    public static final int GOOGLE_EARTH_LAYER_WIKIPEDIA = 3;
    private static final String GOOGLE_EARTH_VISIBLE_LAYER = "earth.visible.layer";
    private static final int[] GOOGLE_EARTH_VISIBLE_LAYER_DEFAULT = new int[]{0, 1, 2, 3};
    private static final String LANE_GUIDANCE = "laneguidance";
    private static final String MAP_IN_KOMBI_PERSPECTIVE = "kombi.perspective";
    private static final int MAP_IN_KOMBI_PERSPECTIVE_DEFAULT = 2;
    private static final String MAIN_MAP_CAR_POSITION = "carpos";
    private static final Point MAIN_MAP_CAR_POSITION_DEFAULT = new Point(400, 200);
    private static final String MAIN_MAP_CONTENT = "content";
    private static final int MAIN_MAP_CONTENT_DEFAULT = 0;
    private static final String MAIN_MAP_LAST_MAP_TYPE = "last.map.type";
    private static final int MAIN_MAP_LAST_MAP_TYPE_DEFAULT = 0;
    private static final String MAIN_MAP_MAP_MODE = "map.mode";
    private static final int MAIN_MAP_MAP_MODE_DEFAULT = 1;
    private static final String MAIN_MAP_ORIENTATION = "orientation";
    private static final int MAIN_MAP_ORIENTATION_DEFAULT = 0;
    private static final String MAIN_MAP_SHOW_ICONS_BRANDS = "show.icons.brands";
    private static final String MAIN_MAP_SHOW_ICONS_FAVORITES = "show.icons.favorites";
    private static final String MAIN_MAP_SHOW_ICONS_POIS = "show.icons.pois";
    private static final boolean MAIN_MAP_SHOW_ICONS_POIS_DEFAULT = true;
    private static final String MAIN_MAP_LOCATED_IN_ABT = "map.located.abt";
    private static final boolean MAIN_MAP_LOCATED_IN_ABT_DEFAULT = true;
    private static final String MAIN_MAP_LOCATED_IN_KOMBI = "map.located.kombi";
    private static final boolean MAIN_MAP_LOCATED_IN_KOMBI_DEFAULT = false;
    private static final String MAIN_MAP_ZOOM_LEVEL = "zoomlevel";
    private static final String KOMBI_MAP_ZOOM_LEVEL = "zoomlevelKombi";
    private static final String KOMBI_MAP_AUTOZOOM = "autozoomKombi";
    private static final int MAIN_MAP_ZOOM_LEVEL_DEFAULT = 10000;
    public static final int KOMBI_MAP_ZOOM_LEVEL_DEFAULT = 10000;
    private static final boolean KOMBI_MAP_AUTOZOOM_DEFAULT = true;
    private static final String MAP_IN_MAP_CAR_POSITION = "carpos";
    private static final Point MAP_IN_MAP_CAR_POSITION_DEFAULT = new Point(50, 100);
    private static final String MAP_IN_MAP_MODE = "mode";
    private static final int MAP_IN_MAP_MODE_DEFAULT = 1;
    private static final String MAP_IN_MAP_ORIENTATION = "orientation";
    private static final int MAP_IN_MAP_ORIENTATION_DEFAULT = 0;
    private static final String MAP_IN_MAP_VIEW_PORT = "viewport";
    private static final Rect MAP_IN_MAP_VIEW_PORT_DEFAULT = new Rect(0, 0, 100, 200);
    private static final String MAP_IN_MAP_ZOOM_LEVEL = "zoomlevel";
    private static final int MAP_IN_MAP_ZOOM_LEVEL_DEFAULT = 20000;
    private static final String MOBILITY_HORIZON_CONSIDERED_LOCATION_TYPES = "considered.location.types";
    private static final int[] MOBILITY_HORIZON_CONSIDERED_LOCATION_TYPES_DEFAULT = new int[]{1};
    private static final String SPLIT_SCREEN_CONTENT_GUIDANCE = "content.guidance";
    private static final int SPLIT_SCREEN_CONTENT_GUIDANCE_DEFAULT = IPersistenceDefaults.HMI_SPLIT_SCREEN_GUIDANCE_CONTENT_DEFAULT;
    private static final String SPLIT_SCREEN_CONTENT_GUIDANCE_NO = "content.guidance.no";
    private static final int SPLIT_SCREEN_CONTENT_GUIDANCE_NO_DEFAULT = IPersistenceDefaults.HMI_SPLIT_SCREEN_NO_GUIDANCE_CONTENT_DEFAULT;
    private static final String SPLIT_SCREEN_GUIDANCE = "guidance";
    private static final boolean SPLIT_SCREEN_GUIDANCE_DEFAULT = IPersistenceDefaults.HMI_SPLIT_SCREEN_GUIDANCE_VISIBILITY_DEFAULT;
    private static final String SPLIT_SCREEN_GUIDANCE_NO = "guidance.no";
    private static final boolean SPLIT_SCREEN_GUIDANCE_NO_DEFAULT = IPersistenceDefaults.HMI_SPLIT_SCREEN_NO_GUIDANCE_VISIBILITY_DEFAULT;
    private static final int HMI_MAIN_MAP_AUTOZOOM_OFF = 0;
    private static final int HMI_MAIN_MAP_AUTOZOOM_ON = 1;
    private PersistableMap persistableMap = ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getExtendedNavPersistence().getPersistableMap("map");
    private PersistableMap persistableMapAutozoom = this.persistableMap.getPersistableMap("autozoom");
    private PersistableMap persistableMapDualscreen = this.persistableMap.getPersistableMap("dualscreen");
    private PersistableMap persistableMapGoogle = this.persistableMap.getPersistableMap("google");
    private PersistableMap persistableMapMainMap = this.persistableMap.getPersistableMap("mainmap");
    private PersistableMap persistableMapKombi = this.persistableMap.getPersistableMap("kombimap");
    private PersistableMap persistableMapMapInMap = this.persistableMap.getPersistableMap("mapinmap");
    private PersistableMap persistableMapMobilityHorizon = this.persistableMap.getPersistableMap("mobilityhorizon");
    private PersistableMap persistableMapSplitscreen = this.persistableMap.getPersistableMap("splitscreen");

    public static final PersistedMapSetup getInstance() {
        return Holder.INSTANCE;
    }

    PersistedMapSetup() {
        for (int i = 0; i < DUALSCREEN_VISIBILITIES_DEFAULT.length; ++i) {
            PersistedMapSetup.DUALSCREEN_VISIBILITIES_DEFAULT[i] = 1;
        }
        ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().addReloadPersistedDataListener(this);
    }

    public void clear() {
        this.persistableMap.clear();
    }

    public int getAutoZoomRecommendedZoomLast() {
        int n = this.persistableMapAutozoom.getInt(AUTOZOOM_RECOMMENDED_ZOOM_LAST, 10000);
        n = (int)MapViewerUtils.checkZoomLevelIsInRange(n);
        return n;
    }

    public int[] getDualScreenVisibilities() {
        return this.persistableMapDualscreen.getIntArray(DUALSCREEN_VISIBILITIES, DUALSCREEN_VISIBILITIES_DEFAULT);
    }

    public int[] getGoogleEarthVisibleLayer() {
        return this.persistableMapGoogle.getIntArray(GOOGLE_EARTH_VISIBLE_LAYER, GOOGLE_EARTH_VISIBLE_LAYER_DEFAULT);
    }

    public int getMapInKombiPerspective() {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            return ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().getMapOrientationKombiFpk();
        }
        return this.persistableMap.getInt(MAP_IN_KOMBI_PERSPECTIVE, 2);
    }

    public Point getMainMapCarPosition() {
        return this.persistableMapMainMap.getPoint("carpos", MAIN_MAP_CAR_POSITION_DEFAULT);
    }

    public int getMainMapContent() {
        return this.persistableMapMainMap.getInt(MAIN_MAP_CONTENT, 0);
    }

    public int getMainMapMapTypeLast() {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            return ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().getMainMapTypeLast();
        }
        return this.persistableMapMainMap.getInt(MAIN_MAP_LAST_MAP_TYPE, 0);
    }

    public int getMainMapMapMode() {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            return ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().getMainMapMapMode();
        }
        return this.persistableMapMainMap.getInt(MAIN_MAP_MAP_MODE, 1);
    }

    public int getMainMapPerspective() {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            return ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().getMainMapOrientation();
        }
        return this.persistableMapMainMap.getInt("orientation", 0);
    }

    public int getKombiMapZoomLevel() {
        int n = this.persistableMapKombi.getInt(KOMBI_MAP_ZOOM_LEVEL, 10000);
        n = (int)MapViewerUtils.checkZoomLevelIsInRange(n);
        return n;
    }

    public boolean getKombiMapAutoZoom() {
        return this.persistableMapKombi.getBoolean(KOMBI_MAP_AUTOZOOM, true);
    }

    public int getMainMapZoomLevel() {
        int n = this.persistableMapMainMap.getInt("zoomlevel", 10000);
        n = (int)MapViewerUtils.checkZoomLevelIsInRange(n);
        return n;
    }

    public Point getMapInMapCarPosition() {
        return this.persistableMapMapInMap.getPoint("carpos", MAP_IN_MAP_CAR_POSITION_DEFAULT);
    }

    public int getMapInMapMode() {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            return ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().getMapInMapMode();
        }
        return this.persistableMapMapInMap.getInt(MAP_IN_MAP_MODE, 1);
    }

    public int getMapInMapOrientation() {
        return this.persistableMapMapInMap.getInt("orientation", 0);
    }

    public Rect getMapInMapScreenViewPort() {
        return this.persistableMapMapInMap.getRect(MAP_IN_MAP_VIEW_PORT, MAP_IN_MAP_VIEW_PORT_DEFAULT);
    }

    public int getMapInMapZoomLevel() {
        return this.persistableMapMapInMap.getInt("zoomlevel", 20000);
    }

    public int[] getMobilityHorizonConsideredLocationTypes() {
        return this.persistableMapMobilityHorizon.getIntArray(MOBILITY_HORIZON_CONSIDERED_LOCATION_TYPES, MOBILITY_HORIZON_CONSIDERED_LOCATION_TYPES_DEFAULT);
    }

    public int getSplitScreenContentGuidance() {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            return ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().getSplitScreenGuidanceContent();
        }
        return this.persistableMapSplitscreen.getInt(SPLIT_SCREEN_CONTENT_GUIDANCE, SPLIT_SCREEN_CONTENT_GUIDANCE_DEFAULT);
    }

    public int getSplitScreenContentNoGuidance() {
        int n = 1;
        n = ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE") ? ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().getSplitScreenNoGuidanceContent() : this.persistableMapSplitscreen.getInt(SPLIT_SCREEN_CONTENT_GUIDANCE_NO, SPLIT_SCREEN_CONTENT_GUIDANCE_NO_DEFAULT);
        if (n < 0 || n > 5) {
            ServiceManager.logger.error(16384).append("SPLIT_SCREEN_CONTENT_GUIDANCE_NO out of range: ").append(n).append(" setting to: ").append(1).log();
            n = 1;
            this.setSplitScreenContentNoGuidance(n);
        }
        return n;
    }

    public int getMainMapAutoZoomMode() {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            return ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().getMainMapAutoZoomMode();
        }
        return this.persistableMapAutozoom.getInt(AUTOZOOM_MAIN_MAP, 1);
    }

    public boolean isAutoZoomMapInMap() {
        return this.persistableMapAutozoom.getBoolean(AUTOZOOM_MAP_IN_MAP, true);
    }

    public boolean isLaneGuidance() {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            return ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().isMapMainLaneGuidance();
        }
        return this.persistableMapMainMap.getBoolean(LANE_GUIDANCE, true);
    }

    public boolean isMainMapShowBrandIcons() {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            return ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().isMapMainMapShowBrandIcons();
        }
        return this.persistableMapMainMap.getBoolean(MAIN_MAP_SHOW_ICONS_BRANDS, true);
    }

    public boolean isMainMapShowFavoritesIcons() {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            return ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().isMapMainMapShowFavoriteIcons();
        }
        return this.persistableMapMainMap.getBoolean(MAIN_MAP_SHOW_ICONS_FAVORITES, true);
    }

    public boolean isMainMapShowPoiIcons() {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            return ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().isMainMapShowPoiIcons();
        }
        return this.persistableMapMainMap.getBoolean(MAIN_MAP_SHOW_ICONS_POIS, true);
    }

    public boolean isMapLocatedInABT() {
        return this.persistableMapMainMap.getBoolean(MAIN_MAP_LOCATED_IN_ABT, true);
    }

    public boolean isMapLocatedInKombi() {
        return this.persistableMapMainMap.getBoolean(MAIN_MAP_LOCATED_IN_KOMBI, false);
    }

    public boolean isSplitScreenGuidance() {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            return ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().isSplitScreenGuidanceVisible();
        }
        return this.persistableMapSplitscreen.getBoolean(SPLIT_SCREEN_GUIDANCE, SPLIT_SCREEN_GUIDANCE_DEFAULT);
    }

    public boolean isSplitScreenNoGuidance() {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            return ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().isSplitScreenNoGuidanceVisible();
        }
        return this.persistableMapSplitscreen.getBoolean(SPLIT_SCREEN_GUIDANCE_NO, SPLIT_SCREEN_GUIDANCE_NO_DEFAULT);
    }

    public void reloadPersistedData() {
    }

    public void setMainMapAutoZoomMode(int n) {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setMainMapAutoZoomMode(n);
        } else {
            this.persistableMapAutozoom.setInt(AUTOZOOM_MAIN_MAP, n);
        }
    }

    public void setAutoZoomMainMap(boolean bl) {
        if (bl) {
            this.setMainMapAutoZoomMode(1);
        } else {
            this.setMainMapAutoZoomMode(0);
        }
    }

    public void setAutoZoomMapInMap(boolean bl) {
        this.persistableMapAutozoom.setBoolean(AUTOZOOM_MAP_IN_MAP, bl);
    }

    public void setAutozoomRecommendedZoomLast(int n) {
        this.persistableMapAutozoom.setInt(AUTOZOOM_RECOMMENDED_ZOOM_LAST, n);
        this.persistableMapAutozoom.setSurviving(AUTOZOOM_RECOMMENDED_ZOOM_LAST, true);
    }

    public void setDualScreenVisibilities(int[] nArray) {
    }

    public void setGoogleEarthVisibleLayer(int[] nArray) {
        this.persistableMapGoogle.setIntArray(GOOGLE_EARTH_VISIBLE_LAYER, nArray);
    }

    public void setLaneGuidance(boolean bl) {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setMapMainLaneGuidance(bl);
        } else {
            this.persistableMapMainMap.setBoolean(LANE_GUIDANCE, bl);
        }
    }

    public void setMainMapCarPosition(Point point) {
        this.persistableMapMainMap.setPoint("carpos", point);
    }

    public void setMainMapContent(int n) {
        this.persistableMapMainMap.setInt(MAIN_MAP_CONTENT, n);
    }

    public void setMainMapLastMapType(int n) {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setMainMapTypeLast(n);
        } else {
            this.persistableMapMainMap.setInt(MAIN_MAP_LAST_MAP_TYPE, n);
        }
    }

    public void setMainMapOrientation(int n) {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setMainMapOrientation(n);
        } else {
            this.persistableMapMainMap.setInt("orientation", n);
        }
    }

    public void setMainMapShowBrandIcons(boolean bl) {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setMapMainMapShowBrandIcons(bl);
        } else {
            this.persistableMapMainMap.setBoolean(MAIN_MAP_SHOW_ICONS_BRANDS, bl);
        }
    }

    public void setMainMapShowFavorites(boolean bl) {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setMapMainMapShowFavoriteIcons(bl);
        } else {
            this.persistableMapMainMap.setBoolean(MAIN_MAP_SHOW_ICONS_FAVORITES, bl);
        }
    }

    public void setMainMapShowPoiIcons(boolean bl) {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setMainMapShowPoiIcons(bl);
        } else {
            this.persistableMapMainMap.setBoolean(MAIN_MAP_SHOW_ICONS_POIS, bl);
        }
    }

    public void setMainMapLocatedInAbt(boolean bl) {
        this.persistableMapMainMap.setBoolean(MAIN_MAP_LOCATED_IN_ABT, bl);
    }

    public void setMainMapLocatedInKombi(boolean bl) {
        this.persistableMapMainMap.setBoolean(MAIN_MAP_LOCATED_IN_KOMBI, bl);
    }

    public void setMainMapMapMode(int n) {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setMainMapMode(n);
        } else {
            this.persistableMapMainMap.setInt(MAIN_MAP_MAP_MODE, n);
        }
    }

    public void setKombiMapAutoZoom(boolean bl) {
        this.persistableMapKombi.setBoolean(KOMBI_MAP_AUTOZOOM, bl);
    }

    public void setKombiMapZoomLevel(int n) {
        this.persistableMapKombi.setInt(KOMBI_MAP_ZOOM_LEVEL, n);
    }

    public void setMainMapZoomLevel(int n) {
        this.persistableMapMainMap.setInt("zoomlevel", n);
    }

    public void setMapInMapCarPosition(Point point) {
        this.persistableMapMapInMap.setPoint("carpos", point);
    }

    public void setMapInMapMode(int n) {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setMapInMapMode(n);
        } else {
            this.persistableMapMapInMap.setInt(MAP_IN_MAP_MODE, n);
        }
    }

    public void setMapInMapOrientation(int n) {
        this.persistableMapMapInMap.setInt("orientation", n);
    }

    public void setMapInMapScreenViewPort(Rect rect) {
        this.persistableMapMapInMap.setRect(MAP_IN_MAP_VIEW_PORT, rect);
    }

    public void setMapInMapZoomLevel(int n) {
        this.persistableMapMapInMap.setInt("zoomlevel", n);
    }

    public void setMobilityHorizonConsideredLocationTypes(int[] nArray) {
        this.persistableMapMobilityHorizon.setIntArray(MOBILITY_HORIZON_CONSIDERED_LOCATION_TYPES, nArray);
    }

    public void setMapInKombiPerspective(int n) {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setMapOrientationKombiFpk(n);
        } else {
            this.persistableMap.setInt(MAP_IN_KOMBI_PERSPECTIVE, n);
        }
    }

    public void setSplitScreenContentGuidance(int n) {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setSplitScreenGuidanceContent(n);
        } else {
            this.persistableMapSplitscreen.setInt(SPLIT_SCREEN_CONTENT_GUIDANCE, n);
        }
    }

    public void setSplitScreenContentNoGuidance(int n) {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setSplitScreenNoGuidanceContent(n);
        } else {
            this.persistableMapSplitscreen.setInt(SPLIT_SCREEN_CONTENT_GUIDANCE_NO, n);
        }
    }

    public void setSplitScreenGuidance(boolean bl) {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setSplitScreenGuidanceVisibility(bl);
        } else {
            this.persistableMapSplitscreen.setBoolean(SPLIT_SCREEN_GUIDANCE, bl);
        }
    }

    public void setSplitScreenNoGuidance(boolean bl) {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setSplitScreenNoGuidanceVisibility(bl);
        } else {
            this.persistableMapSplitscreen.setBoolean(SPLIT_SCREEN_GUIDANCE_NO, bl);
        }
    }

    public boolean isAutoZoomMainMap() {
        return this.getMainMapAutoZoomMode() == 1;
    }

    public void setDayNightModeMainMap(int n) {
        ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setDayNightMainMapMode(n);
    }

    public int getDayNightModeMainMap() {
        return ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().getDayNightMainMapMode();
    }

    private static class Holder {
        public static final PersistedMapSetup INSTANCE = new PersistedMapSetup();

        private Holder() {
        }
    }
}

