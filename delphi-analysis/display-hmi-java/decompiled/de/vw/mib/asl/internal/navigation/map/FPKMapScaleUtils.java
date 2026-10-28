/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map;

import de.vw.mib.asl.api.navigation.util.ASLNavigationUtilFactory;
import de.vw.mib.asl.api.navigation.util.IExtLogger;
import de.vw.mib.desktop.internal.common.ServiceManager;
import java.util.SortedMap;
import java.util.TreeMap;

public final class FPKMapScaleUtils {
    private static IExtLogger LOGGER = ASLNavigationUtilFactory.getNavigationUtilApi().getExtLogger(65536, "[FPKMapScaleUtils]");

    public static ZoomLevelThreshold getFPKMapScaleThreshold(int n) {
        return ZoomLevelThreshold.getCorrespondingLevel(n);
    }

    public static class ZoomLevelThreshold {
        private static final int ID_DEFAULT = 0;
        private static final int ID_METER = 0;
        private static final int ID_KM = 1;
        private static final int ID_KM_FLOATING = 6;
        private static final int ID_YARD = 2;
        private static final int ID_FOOT = 3;
        private static final int ID_MILE = 4;
        private static final int ID_MILE_FLOATING = 7;
        private static final TreeMap THRESHOLDS = new TreeMap();
        public final int zoomMetric;
        public final int zoomImperial;
        public final int unitMetric;
        public final int unitImperial;

        private ZoomLevelThreshold(int n, int n2, int n3, int n4) {
            this.zoomMetric = n;
            this.zoomImperial = n2;
            this.unitMetric = n3;
            this.unitImperial = n4;
        }

        private ZoomLevelThreshold() {
            this.zoomImperial = 0;
            this.zoomMetric = 0;
            this.unitImperial = 0;
            this.unitMetric = 0;
        }

        private static void setupZoomStep(int n, int n2, int n3, String string, int n4, String string2, int n5, String string3, int n6) {
            boolean bl = ServiceManager.configurationManager.isFeatureFlagSet(155);
            ZoomLevelThreshold.setupZoomStep(n, n2, n3, string, n4, bl ? string2 : string3, bl ? n5 : n6);
        }

        private static void setupZoomStep(int n, int n2, int n3, String string, int n4, String string2, int n5) {
            try {
                int n6 = (int)(Float.parseFloat(string) * 10.0f);
                int n7 = (int)(Float.parseFloat(string2) * 10.0f);
                THRESHOLDS.put(new Integer(n2), new ZoomLevelThreshold(n6, n7, n4, n5));
            }
            catch (Exception exception) {
                LOGGER.error("Routine problem occured when calculating getCorrespondingLevel(int)");
            }
        }

        static ZoomLevelThreshold getCorrespondingLevel(int n) {
            ZoomLevelThreshold zoomLevelThreshold = new ZoomLevelThreshold();
            SortedMap sortedMap = THRESHOLDS.tailMap(new Integer(n));
            Integer n2 = sortedMap.firstKey();
            if (n2 != null) {
                try {
                    zoomLevelThreshold = (ZoomLevelThreshold)THRESHOLDS.get(n2);
                }
                catch (NumberFormatException numberFormatException) {
                    LOGGER.error("Routine problem occured when calculating getCorrespondingLevel(int)");
                }
            }
            return zoomLevelThreshold;
        }

        static {
            ZoomLevelThreshold.setupZoomStep(0, 20, 18, "20", 0, "20", 2, "60", 3);
            ZoomLevelThreshold.setupZoomStep(1, 30, 28, "30", 0, "30", 2, "100", 3);
            ZoomLevelThreshold.setupZoomStep(2, 50, 46, "50", 0, "50", 2, "150", 3);
            ZoomLevelThreshold.setupZoomStep(3, 75, 69, "75", 0, "75", 2, "200", 3);
            ZoomLevelThreshold.setupZoomStep(4, 100, 91, "100", 0, "100", 2, "300", 3);
            ZoomLevelThreshold.setupZoomStep(5, 150, 137, "150", 0, "150", 2, "500", 3);
            ZoomLevelThreshold.setupZoomStep(6, 200, 183, "200", 0, "200", 2, "650", 3);
            ZoomLevelThreshold.setupZoomStep(7, 300, 274, "300", 0, "300", 2, "0.2", 7);
            ZoomLevelThreshold.setupZoomStep(8, 400, 366, "400", 0, "400", 2, "0.25", 7);
            ZoomLevelThreshold.setupZoomStep(9, 500, 457, "500", 0, "500", 2, "0.3", 7);
            ZoomLevelThreshold.setupZoomStep(10, 750, 686, "750", 0, "750", 2, "0.5", 7);
            ZoomLevelThreshold.setupZoomStep(11, 1000, 1127, "1", 1, "0.7", 7);
            ZoomLevelThreshold.setupZoomStep(12, 1500, 1609, "1.5", 6, "1", 4);
            ZoomLevelThreshold.setupZoomStep(13, 2000, 2414, "2", 1, "1.5", 7);
            ZoomLevelThreshold.setupZoomStep(14, 2500, 2414, "2.5", 6, "1.5", 7);
            ZoomLevelThreshold.setupZoomStep(15, 3000, 3219, "3", 1, "2", 4);
            ZoomLevelThreshold.setupZoomStep(16, 4000, 4023, "4", 1, "2.5", 7);
            ZoomLevelThreshold.setupZoomStep(17, 5000, 4828, "5", 1, "3", 4);
            ZoomLevelThreshold.setupZoomStep(18, 6000, 6437, "6", 1, "4", 4);
            ZoomLevelThreshold.setupZoomStep(19, 7000, 6437, "7", 1, "4", 4);
            ZoomLevelThreshold.setupZoomStep(20, 8000, 8047, "8", 1, "5", 4);
            ZoomLevelThreshold.setupZoomStep(21, 9000, 8047, "9", 1, "5", 4);
            ZoomLevelThreshold.setupZoomStep(22, 10000, 11265, "10", 1, "7", 4);
            ZoomLevelThreshold.setupZoomStep(23, 15000, 16093, "15", 1, "10", 4);
            ZoomLevelThreshold.setupZoomStep(24, 20000, 24140, "20", 1, "15", 4);
            ZoomLevelThreshold.setupZoomStep(25, 30000, 32187, "30", 1, "20", 4);
            ZoomLevelThreshold.setupZoomStep(26, 40000, 40234, "40", 1, "25", 4);
            ZoomLevelThreshold.setupZoomStep(27, 50000, 48280, "50", 1, "30", 4);
            ZoomLevelThreshold.setupZoomStep(28, 60000, 64374, "60", 1, "40", 4);
            ZoomLevelThreshold.setupZoomStep(29, 70000, 64374, "70", 1, "40", 4);
            ZoomLevelThreshold.setupZoomStep(30, 80000, 80467, "80", 1, "50", 4);
            ZoomLevelThreshold.setupZoomStep(31, 90000, 80467, "90", 1, "50", 4);
            ZoomLevelThreshold.setupZoomStep(32, 100000, 112654, "100", 1, "70", 4);
            ZoomLevelThreshold.setupZoomStep(33, 125000, 128748, "125", 1, "80", 4);
            ZoomLevelThreshold.setupZoomStep(34, 150000, 160934, "150", 1, "100", 4);
            ZoomLevelThreshold.setupZoomStep(35, 175000, 201168, "175", 1, "125", 4);
            ZoomLevelThreshold.setupZoomStep(36, 200000, 241402, "200", 1, "150", 4);
            ZoomLevelThreshold.setupZoomStep(37, 250000, 241402, "250", 1, "150", 4);
            ZoomLevelThreshold.setupZoomStep(38, 300000, 321869, "300", 1, "200", 4);
            ZoomLevelThreshold.setupZoomStep(39, 400000, 402336, "400", 1, "250", 4);
            ZoomLevelThreshold.setupZoomStep(40, 500000, 482803, "500", 1, "300", 4);
            ZoomLevelThreshold.setupZoomStep(41, 600000, 643738, "600", 1, "400", 4);
            ZoomLevelThreshold.setupZoomStep(42, 700000, 724205, "700", 1, "450", 4);
            ZoomLevelThreshold.setupZoomStep(43, 800000, 804672, "800", 1, "500", 4);
            ZoomLevelThreshold.setupZoomStep(44, 1000000, 965606, "1000", 1, "600", 4);
            ZoomLevelThreshold.setupZoomStep(45, 1500000, 1609344, "1500", 1, "1000", 4);
            ZoomLevelThreshold.setupZoomStep(46, 2000000, 2011680, "2000", 1, "1250", 4);
            ZoomLevelThreshold.setupZoomStep(47, 2500000, 2414016, "2500", 1, "1500", 4);
        }
    }
}

