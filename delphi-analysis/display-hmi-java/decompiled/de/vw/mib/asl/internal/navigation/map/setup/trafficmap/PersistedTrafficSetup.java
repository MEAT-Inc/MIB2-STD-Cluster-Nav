/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.setup.trafficmap;

import de.vw.mib.asl.api.navigation.util.ASLNavigationUtilFactory;
import de.vw.mib.asl.api.navigation.util.PersistableMap;

public class PersistedTrafficSetup {
    private static final String MAIN_MAP_SHOW_SPEED_AND_FLOW = "show.speedandflow";
    private static final boolean MAIN_MAP_SHOW_SPEED_AND_FLOW_DEFAULT = true;
    private static final String SHOW_CONGESTIONS = "show.congestions";
    private static final boolean SHOW_CONGESTIONS_DEFAULT = true;
    private static final String SHOW_FREE_FLOW = "show.freeflow";
    private static final boolean SHOW_FREE_FLOW_DEFAULT = true;
    private static final String SHOW_INCIDENTS = "show.incidents";
    private static final boolean SHOW_INCIDENTS_DEFAULT = true;
    private static final String SPEED_AND_FLOW_ROAD_CLASS = "speedAndFlow.roadClass";
    private static final int SPEED_AND_FLOW_ROAD_CLASS_DEFAULT = 3;
    private PersistableMap persistableMap = ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getExtendedNavPersistence().getPersistableMap("traffic");

    public static final PersistedTrafficSetup getInstance() {
        return Holder.INSTANCE;
    }

    public void clear() {
        this.persistableMap.clear();
        ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setTrafficShowCongestion(true);
        ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setTrafficShowFreeFlow(true);
        ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setTrafficShowIncidents(true);
        ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setMainMapShowSpeedAndFlow(true);
    }

    public int getSpeedAndFlowRoadClass() {
        return this.persistableMap.getInt(SPEED_AND_FLOW_ROAD_CLASS, 3);
    }

    public int getSpeedAndFlowRoadClassDSI() {
        int n = this.getSpeedAndFlowRoadClass();
        switch (n) {
            case 0: {
                return 4;
            }
            case 1: {
                return 1;
            }
            case 2: {
                return 2;
            }
            case 3: {
                return 3;
            }
        }
        return 3;
    }

    public boolean getTrafficShowCongestion() {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            return ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().getTrafficShowCongestion();
        }
        return this.persistableMap.getBoolean(SHOW_CONGESTIONS, true);
    }

    public boolean getTrafficShowFreeFlow() {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            return ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().getTrafficShowFreeFlow();
        }
        return this.persistableMap.getBoolean(SHOW_FREE_FLOW, true);
    }

    public boolean getTrafficShowIncidents() {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            return ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().getTrafficShowIncidents();
        }
        return this.persistableMap.getBoolean(SHOW_INCIDENTS, true);
    }

    public boolean isMainMapShowSpeedAndFlow() {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            return ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().getMainMapShowSpeedAndFlow();
        }
        return this.persistableMap.getBoolean(MAIN_MAP_SHOW_SPEED_AND_FLOW, true);
    }

    public void setMainMapShowSpeedAndFlow(boolean bl) {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setMainMapShowSpeedAndFlow(bl);
        } else {
            this.persistableMap.setBoolean(MAIN_MAP_SHOW_SPEED_AND_FLOW, bl);
        }
    }

    public void setSpeedAndFlowRoadClass(int n) {
        this.persistableMap.setInt(SPEED_AND_FLOW_ROAD_CLASS, n);
    }

    public void setTrafficShowCongestion(boolean bl) {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setTrafficShowCongestion(bl);
        } else {
            this.persistableMap.setBoolean(SHOW_CONGESTIONS, bl);
        }
    }

    public void setTrafficShowFreeFlow(boolean bl) {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setTrafficShowFreeFlow(bl);
        } else {
            this.persistableMap.setBoolean(SHOW_FREE_FLOW, bl);
        }
    }

    public void setTrafficShowIncidents(boolean bl) {
        if (ASLNavigationUtilFactory.getNavigationUtilApi().getDebugFlags().getASLDebugFlag("NEW_NAV_PERSISTENCE")) {
            ASLNavigationUtilFactory.getNavigationUtilApi().getNavigationDp().getPersonalNaviPersistence().setTrafficShowIncidents(bl);
        } else {
            this.persistableMap.setBoolean(SHOW_INCIDENTS, bl);
        }
    }

    private static class Holder {
        public static final PersistedTrafficSetup INSTANCE = new PersistedTrafficSetup();

        private Holder() {
        }
    }
}

