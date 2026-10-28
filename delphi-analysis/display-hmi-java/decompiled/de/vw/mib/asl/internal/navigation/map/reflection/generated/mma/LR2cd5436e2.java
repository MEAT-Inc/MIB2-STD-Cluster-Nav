/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.reflection.generated.mma;

import de.vw.mib.asl.api.navigation.ILocationWrapper;
import de.vw.mib.asl.api.navigation.map.ASLNavigationMapConfiguration;
import de.vw.mib.asl.api.navigation.map.MapConfiguration;
import de.vw.mib.asl.internal.navigation.map.asl.service.ASLNavigationServiceMainMapFactory;
import de.vw.mib.asl.internal.navigation.map.asl.service.ASLNavigationServiceMainMapTarget;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.adbedit.DSIAdbEditTarget;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.google.earth.DSIMapViewerGoogleCtrlTarget;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.google.license.GoogleEarthLicenseTargetHSM;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.google.streetview.DSIMapViewerStreetViewCtrlTarget;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.mapviewer.getinfoforscreenposition.DSIMapViewerGetInfoForScreenPositionTargetHSM;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.mapviewer.status.DSIMapViewerStatusTarget;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.mapviewer.switchmapviewer.DSIMapViewerControlSwitchMapviewerTargetHSM;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.mobilityhorizon.DSIMobilityHorizonTarget;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.navigation.DSINavigationTarget;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.zoomengine.DSIMapViewerZoomEngineTarget;
import de.vw.mib.asl.internal.navigation.map.kombi.MapViewerKombiTargetHSM;
import de.vw.mib.asl.internal.navigation.map.mainmap.MapViewerTargetHSM;
import de.vw.mib.asl.internal.navigation.map.mainmap.autozoom.MapViewerAutoZoomTargetHSM;
import de.vw.mib.asl.internal.navigation.map.mainmap.content.MapContentChangerTargetHSM;
import de.vw.mib.asl.internal.navigation.map.mainmap.destinput.gps.GPSInputTargetHSM;
import de.vw.mib.asl.internal.navigation.map.mainmap.duallistview.DualListViewHsmTarget;
import de.vw.mib.asl.internal.navigation.map.mainmap.focus.MapViewerFocusTargetHSM;
import de.vw.mib.asl.internal.navigation.map.mainmap.google.streetview.MapViewerStreetviewTargetHSM;
import de.vw.mib.asl.internal.navigation.map.mainmap.hknav.MapViewerHKNavTargetHSM;
import de.vw.mib.asl.internal.navigation.map.mainmap.mapswitch.MapViewerMapSwitchTargetHSM;
import de.vw.mib.asl.internal.navigation.map.mainmap.perspectives.MapViewerPerspectivesTargetHSM;
import de.vw.mib.asl.internal.navigation.map.mainmap.rocketzoom.MapViewerRocketzoomTargetHSM;
import de.vw.mib.asl.internal.navigation.map.mainmap.rubberband.RubberBandHsmTarget;
import de.vw.mib.asl.internal.navigation.map.mainmap.touchapproach.TouchApproachTarget;
import de.vw.mib.asl.internal.navigation.map.mainmap.touchgestures.MapViewerTouchgesturesTargetHSM;
import de.vw.mib.asl.internal.navigation.map.mapinmap.MapInMapViewerTargetHsm;
import de.vw.mib.asl.internal.navigation.map.mapinmap.perspectives.MapInMapViewerPerspectivesTargetHsm;
import de.vw.mib.asl.internal.navigation.map.setup.MapSetupTargetHSM;
import de.vw.mib.asl.internal.navigation.map.setup.google.earth.GoogleEarthSetupTargetHSM;
import de.vw.mib.asl.internal.navigation.map.setup.mobilityhorizon.MobilityHorizonSetupHsmTarget;
import de.vw.mib.asl.internal.navigation.map.setup.trafficmap.TrafficMapSetupHsmTarget;
import de.vw.mib.genericevents.AbstractTarget;
import de.vw.mib.genericevents.EventGeneric;
import de.vw.mib.reflection.MultipleMethodAccessibleObject;
import de.vw.mib.reflection.RuntimeUtil;
import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import org.dsi.ifc.map.DSIMapViewerControl;
import org.dsi.ifc.map.Point;
import org.dsi.ifc.map.PosInfo;

public final class LR2cd5436e2
extends MultipleMethodAccessibleObject {
    private int a0(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 1452019427: {
                if (bl) {
                    if (n2 != 413415144) break;
                    n3 = 0;
                    break;
                }
                n3 = 0;
                break;
            }
        }
        return n3;
    }

    private int a1(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -2136408545: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 4;
                    break;
                }
                n3 = 4;
                break;
            }
            case -2130246088: {
                if (bl) {
                    if (n2 != 105060) break;
                    n3 = 14;
                    break;
                }
                n3 = 14;
                break;
            }
            case -2065259885: {
                if (bl) {
                    if (n2 != 3328241) break;
                    n3 = 27;
                    break;
                }
                n3 = 27;
                break;
            }
            case -2046744643: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 21;
                    break;
                }
                n3 = 21;
                break;
            }
            case -1903013683: {
                if (bl) {
                    if (n2 == 2035629761) {
                        n3 = 5;
                        break;
                    }
                    if (n2 != 135018749) break;
                    n3 = 6;
                    break;
                }
                n3 = 5;
                break;
            }
            case -1814771260: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 29;
                    break;
                }
                n3 = 29;
                break;
            }
            case -1190093268: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 15;
                    break;
                }
                n3 = 15;
                break;
            }
            case -1009470683: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 26;
                    break;
                }
                n3 = 26;
                break;
            }
            case -992138886: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 16;
                    break;
                }
                n3 = 16;
                break;
            }
            case -965536487: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 17;
                    break;
                }
                n3 = 17;
                break;
            }
            case -808405881: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 30;
                    break;
                }
                n3 = 30;
                break;
            }
            case -797420604: {
                if (bl) {
                    if (n2 != 1230281229) break;
                    n3 = 2;
                    break;
                }
                n3 = 2;
                break;
            }
            case -704102565: {
                if (bl) {
                    if (n2 != 64712349) break;
                    n3 = 8;
                    break;
                }
                n3 = 8;
                break;
            }
            case -696285491: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 10;
                    break;
                }
                n3 = 10;
                break;
            }
            case -312405208: {
                if (bl) {
                    if (n2 != 3328241) break;
                    n3 = 18;
                    break;
                }
                n3 = 18;
                break;
            }
            case -110026512: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 11;
                    break;
                }
                n3 = 11;
                break;
            }
            case 97432157: {
                if (bl) {
                    if (n2 != 64712349) break;
                    n3 = 23;
                    break;
                }
                n3 = 23;
                break;
            }
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 1;
                    break;
                }
                n3 = 1;
                break;
            }
            case 213417409: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 20;
                    break;
                }
                n3 = 20;
                break;
            }
            case 416508134: {
                if (bl) {
                    if (n2 != 1173571301) break;
                    n3 = 12;
                    break;
                }
                n3 = 12;
                break;
            }
            case 454050952: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 13;
                    break;
                }
                n3 = 13;
                break;
            }
            case 555497973: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 28;
                    break;
                }
                n3 = 28;
                break;
            }
            case 732666517: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 22;
                    break;
                }
                n3 = 22;
                break;
            }
            case 1400351673: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 24;
                    break;
                }
                n3 = 24;
                break;
            }
            case 1456098328: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 7;
                    break;
                }
                n3 = 7;
                break;
            }
            case 1814031083: {
                if (bl) {
                    if (n2 != 64712349) break;
                    n3 = 19;
                    break;
                }
                n3 = 19;
                break;
            }
            case 1912505853: {
                if (bl) {
                    if (n2 != -137231023) break;
                    n3 = 3;
                    break;
                }
                n3 = 3;
                break;
            }
            case 1933592746: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 25;
                    break;
                }
                n3 = 25;
                break;
            }
            case 1969126943: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 9;
                    break;
                }
                n3 = 9;
                break;
            }
        }
        return n3;
    }

    private int a2(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 31;
                    break;
                }
                n3 = 31;
                break;
            }
            case 1095637282: {
                if (bl) {
                    if (n2 != 413415144) break;
                    n3 = 32;
                    break;
                }
                n3 = 32;
                break;
            }
        }
        return n3;
    }

    private int a3(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 33;
                    break;
                }
                n3 = 33;
                break;
            }
            case 289883349: {
                if (bl) {
                    if (n2 != 413415144) break;
                    n3 = 34;
                    break;
                }
                n3 = 34;
                break;
            }
        }
        return n3;
    }

    private int a4(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -1565593098: {
                if (bl) {
                    if (n2 != 1195260122) break;
                    n3 = 38;
                    break;
                }
                n3 = 38;
                break;
            }
            case -863366187: {
                if (bl) {
                    if (n2 != 64712349) break;
                    n3 = 44;
                    break;
                }
                n3 = 44;
                break;
            }
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 35;
                    break;
                }
                n3 = 35;
                break;
            }
            case 255944253: {
                if (bl) {
                    if (n2 != 64712349) break;
                    n3 = 42;
                    break;
                }
                n3 = 42;
                break;
            }
            case 677102314: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 37;
                    break;
                }
                n3 = 37;
                break;
            }
            case 730463215: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 36;
                    break;
                }
                n3 = 36;
                break;
            }
            case 891817460: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 39;
                    break;
                }
                n3 = 39;
                break;
            }
            case 1096476829: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 43;
                    break;
                }
                n3 = 43;
                break;
            }
            case 1158331180: {
                if (bl) {
                    if (n2 != 64712349) break;
                    n3 = 40;
                    break;
                }
                n3 = 40;
                break;
            }
            case 1834297093: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 41;
                    break;
                }
                n3 = 41;
                break;
            }
        }
        return n3;
    }

    private int a5(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -427171151: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 47;
                    break;
                }
                n3 = 47;
                break;
            }
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 45;
                    break;
                }
                n3 = 45;
                break;
            }
            case 1170054756: {
                if (bl) {
                    if (n2 != 413415144) break;
                    n3 = 46;
                    break;
                }
                n3 = 46;
                break;
            }
        }
        return n3;
    }

    private int a6(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -1767341375: {
                if (bl) {
                    if (n2 != -159319226) break;
                    n3 = 50;
                    break;
                }
                n3 = 50;
                break;
            }
            case -745710279: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 51;
                    break;
                }
                n3 = 51;
                break;
            }
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 48;
                    break;
                }
                n3 = 48;
                break;
            }
            case 317805469: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 49;
                    break;
                }
                n3 = 49;
                break;
            }
        }
        return n3;
    }

    private int a7(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -1742139752: {
                if (bl) {
                    if (n2 != 3890111) break;
                    n3 = 58;
                    break;
                }
                n3 = 58;
                break;
            }
            case -797370196: {
                if (bl) {
                    if (n2 != 105060) break;
                    n3 = 56;
                    break;
                }
                n3 = 56;
                break;
            }
            case -654579608: {
                if (bl) {
                    if (n2 != 3890114) break;
                    n3 = 54;
                    break;
                }
                n3 = 54;
                break;
            }
            case -363569082: {
                if (bl) {
                    if (n2 != 68598940) break;
                    n3 = 57;
                    break;
                }
                n3 = 57;
                break;
            }
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 52;
                    break;
                }
                n3 = 52;
                break;
            }
            case 1149752388: {
                if (bl) {
                    if (n2 != 5057769) break;
                    n3 = 55;
                    break;
                }
                n3 = 55;
                break;
            }
            case 1814031083: {
                if (bl) {
                    if (n2 != 64712349) break;
                    n3 = 53;
                    break;
                }
                n3 = 53;
                break;
            }
        }
        return n3;
    }

    private int a8(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -1127694161: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 64;
                    break;
                }
                n3 = 64;
                break;
            }
            case -427171151: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 60;
                    break;
                }
                n3 = 60;
                break;
            }
            case -177195884: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 66;
                    break;
                }
                n3 = 66;
                break;
            }
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 59;
                    break;
                }
                n3 = 59;
                break;
            }
            case 216730980: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 62;
                    break;
                }
                n3 = 62;
                break;
            }
            case 730151575: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 61;
                    break;
                }
                n3 = 61;
                break;
            }
            case 921366385: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 67;
                    break;
                }
                n3 = 67;
                break;
            }
            case 1072002463: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 65;
                    break;
                }
                n3 = 65;
                break;
            }
            case 1611760732: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 63;
                    break;
                }
                n3 = 63;
                break;
            }
        }
        return n3;
    }

    private int a9(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -1944490167: {
                if (bl) {
                    if (n2 != 413415144) break;
                    n3 = 68;
                    break;
                }
                n3 = 68;
                break;
            }
        }
        return n3;
    }

    private int a10(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -606765403: {
                if (bl) {
                    if (n2 != 413415144) break;
                    n3 = 70;
                    break;
                }
                n3 = 70;
                break;
            }
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 69;
                    break;
                }
                n3 = 69;
                break;
            }
        }
        return n3;
    }

    private int a11(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 71;
                    break;
                }
                n3 = 71;
                break;
            }
            case 2081857788: {
                if (bl) {
                    if (n2 != 413415144) break;
                    n3 = 72;
                    break;
                }
                n3 = 72;
                break;
            }
        }
        return n3;
    }

    private int a12(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -1834602102: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 79;
                    break;
                }
                n3 = 79;
                break;
            }
            case -1815942789: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 82;
                    break;
                }
                n3 = 82;
                break;
            }
            case -1697698876: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 77;
                    break;
                }
                n3 = 77;
                break;
            }
            case -1634311308: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 76;
                    break;
                }
                n3 = 76;
                break;
            }
            case -1408325287: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 81;
                    break;
                }
                n3 = 81;
                break;
            }
            case -824718097: {
                if (bl) {
                    if (n2 != 97526993) break;
                    n3 = 78;
                    break;
                }
                n3 = 78;
                break;
            }
            case -714834490: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 80;
                    break;
                }
                n3 = 80;
                break;
            }
            case -667564320: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 87;
                    break;
                }
                n3 = 87;
                break;
            }
            case -51091826: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 85;
                    break;
                }
                n3 = 85;
                break;
            }
            case 25224473: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 88;
                    break;
                }
                n3 = 88;
                break;
            }
            case 43237226: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 83;
                    break;
                }
                n3 = 83;
                break;
            }
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 73;
                    break;
                }
                n3 = 73;
                break;
            }
            case 730151575: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 74;
                    break;
                }
                n3 = 74;
                break;
            }
            case 1107240587: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 86;
                    break;
                }
                n3 = 86;
                break;
            }
            case 1232867375: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 75;
                    break;
                }
                n3 = 75;
                break;
            }
            case 1848261598: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 84;
                    break;
                }
                n3 = 84;
                break;
            }
        }
        return n3;
    }

    private int a13(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 89;
                    break;
                }
                n3 = 89;
                break;
            }
            case 730463215: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 90;
                    break;
                }
                n3 = 90;
                break;
            }
        }
        return n3;
    }

    private int a14(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 91;
                    break;
                }
                n3 = 91;
                break;
            }
            case 730044910: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 93;
                    break;
                }
                n3 = 93;
                break;
            }
            case 730463215: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 92;
                    break;
                }
                n3 = 92;
                break;
            }
        }
        return n3;
    }

    private int a15(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 94;
                    break;
                }
                n3 = 94;
                break;
            }
            case 156909210: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 95;
                    break;
                }
                n3 = 95;
                break;
            }
        }
        return n3;
    }

    private int a16(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -2018157808: {
                if (bl) {
                    if (n2 != 1173571301) break;
                    n3 = 105;
                    break;
                }
                n3 = 105;
                break;
            }
            case -1282568822: {
                if (bl) {
                    if (n2 != 1181620966) break;
                    n3 = 99;
                    break;
                }
                n3 = 99;
                break;
            }
            case -706779532: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 101;
                    break;
                }
                n3 = 101;
                break;
            }
            case -580471546: {
                if (bl) {
                    if (n2 != -1627316424) break;
                    n3 = 106;
                    break;
                }
                n3 = 106;
                break;
            }
            case -448632341: {
                if (bl) {
                    if (n2 != -46564588) break;
                    n3 = 103;
                    break;
                }
                n3 = 103;
                break;
            }
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 96;
                    break;
                }
                n3 = 96;
                break;
            }
            case 345226207: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 102;
                    break;
                }
                n3 = 102;
                break;
            }
            case 730044910: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 98;
                    break;
                }
                n3 = 98;
                break;
            }
            case 730151575: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 97;
                    break;
                }
                n3 = 97;
                break;
            }
            case 1187986157: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 100;
                    break;
                }
                n3 = 100;
                break;
            }
            case 1576580485: {
                if (bl) {
                    if (n2 != -2135789801) break;
                    n3 = 104;
                    break;
                }
                n3 = 104;
                break;
            }
        }
        return n3;
    }

    private int a17(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 107;
                    break;
                }
                n3 = 107;
                break;
            }
        }
        return n3;
    }

    private int a18(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -183849917: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 113;
                    break;
                }
                n3 = 113;
                break;
            }
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 108;
                    break;
                }
                n3 = 108;
                break;
            }
            case 156909210: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 111;
                    break;
                }
                n3 = 111;
                break;
            }
            case 730044910: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 110;
                    break;
                }
                n3 = 110;
                break;
            }
            case 730151575: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 109;
                    break;
                }
                n3 = 109;
                break;
            }
            case 853365281: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 114;
                    break;
                }
                n3 = 114;
                break;
            }
            case 1044895599: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 112;
                    break;
                }
                n3 = 112;
                break;
            }
            case 1577520579: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 115;
                    break;
                }
                n3 = 115;
                break;
            }
            case 2121684573: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 116;
                    break;
                }
                n3 = 116;
                break;
            }
        }
        return n3;
    }

    private int a19(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -2062126456: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 122;
                    break;
                }
                n3 = 122;
                break;
            }
            case -558060982: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 120;
                    break;
                }
                n3 = 120;
                break;
            }
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 117;
                    break;
                }
                n3 = 117;
                break;
            }
            case 730044910: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 119;
                    break;
                }
                n3 = 119;
                break;
            }
            case 730151575: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 118;
                    break;
                }
                n3 = 118;
                break;
            }
            case 1318953525: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 121;
                    break;
                }
                n3 = 121;
                break;
            }
            case 1322490929: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 124;
                    break;
                }
                n3 = 124;
                break;
            }
            case 1339246438: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 123;
                    break;
                }
                n3 = 123;
                break;
            }
            case 1786096460: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 125;
                    break;
                }
                n3 = 125;
                break;
            }
        }
        return n3;
    }

    private int a20(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 126;
                    break;
                }
                n3 = 126;
                break;
            }
            case 730044910: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 128;
                    break;
                }
                n3 = 128;
                break;
            }
            case 730151575: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 127;
                    break;
                }
                n3 = 127;
                break;
            }
        }
        return n3;
    }

    private int a21(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -553067622: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 135;
                    break;
                }
                n3 = 135;
                break;
            }
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 129;
                    break;
                }
                n3 = 129;
                break;
            }
            case 668722313: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 132;
                    break;
                }
                n3 = 132;
                break;
            }
            case 730044910: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 131;
                    break;
                }
                n3 = 131;
                break;
            }
            case 730463215: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 130;
                    break;
                }
                n3 = 130;
                break;
            }
            case 1086975031: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 134;
                    break;
                }
                n3 = 134;
                break;
            }
            case 1149288556: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 133;
                    break;
                }
                n3 = 133;
                break;
            }
        }
        return n3;
    }

    private int a22(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -1925194550: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 146;
                    break;
                }
                n3 = 146;
                break;
            }
            case -1391977543: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 141;
                    break;
                }
                n3 = 141;
                break;
            }
            case -752992774: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 138;
                    break;
                }
                n3 = 138;
                break;
            }
            case -406511346: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 149;
                    break;
                }
                n3 = 149;
                break;
            }
            case -258086098: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 148;
                    break;
                }
                n3 = 148;
                break;
            }
            case -162298428: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 144;
                    break;
                }
                n3 = 144;
                break;
            }
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 136;
                    break;
                }
                n3 = 136;
                break;
            }
            case 249878488: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 150;
                    break;
                }
                n3 = 150;
                break;
            }
            case 730151575: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 137;
                    break;
                }
                n3 = 137;
                break;
            }
            case 898113590: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 147;
                    break;
                }
                n3 = 147;
                break;
            }
            case 936277630: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 145;
                    break;
                }
                n3 = 145;
                break;
            }
            case 1056184219: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 142;
                    break;
                }
                n3 = 142;
                break;
            }
            case 1586202989: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 143;
                    break;
                }
                n3 = 143;
                break;
            }
            case 1935019917: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 139;
                    break;
                }
                n3 = 139;
                break;
            }
            case 1935019948: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 140;
                    break;
                }
                n3 = 140;
                break;
            }
        }
        return n3;
    }

    private int a23(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 151;
                    break;
                }
                n3 = 151;
                break;
            }
        }
        return n3;
    }

    private int a24(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -1246702903: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 157;
                    break;
                }
                n3 = 157;
                break;
            }
            case -1000943884: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 155;
                    break;
                }
                n3 = 155;
                break;
            }
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 152;
                    break;
                }
                n3 = 152;
                break;
            }
            case 170041121: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 156;
                    break;
                }
                n3 = 156;
                break;
            }
            case 730151575: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 153;
                    break;
                }
                n3 = 153;
                break;
            }
            case 1063253902: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 154;
                    break;
                }
                n3 = 154;
                break;
            }
            case 1309240600: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 159;
                    break;
                }
                n3 = 159;
                break;
            }
            case 1894421678: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 158;
                    break;
                }
                n3 = 158;
                break;
            }
        }
        return n3;
    }

    private int a25(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -823911215: {
                if (bl) {
                    if (n2 != 1418859852) break;
                    n3 = 161;
                    break;
                }
                n3 = 161;
                break;
            }
            case -797625872: {
                if (bl) {
                    if (n2 != 64712349) break;
                    n3 = 162;
                    break;
                }
                n3 = 162;
                break;
            }
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 160;
                    break;
                }
                n3 = 160;
                break;
            }
        }
        return n3;
    }

    private int a26(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 7547832: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 165;
                    break;
                }
                n3 = 165;
                break;
            }
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 163;
                    break;
                }
                n3 = 163;
                break;
            }
            case 712345521: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 164;
                    break;
                }
                n3 = 164;
                break;
            }
        }
        return n3;
    }

    private int a27(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -1634221999: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 167;
                    break;
                }
                n3 = 167;
                break;
            }
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 166;
                    break;
                }
                n3 = 166;
                break;
            }
        }
        return n3;
    }

    private int a28(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a29(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 168;
                    break;
                }
                n3 = 168;
                break;
            }
        }
        return n3;
    }

    private int a30(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -1634221999: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 169;
                    break;
                }
                n3 = 169;
                break;
            }
        }
        return n3;
    }

    private int a31(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a32(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -2071340879: {
                if (bl) {
                    if (n2 != 64712349) break;
                    n3 = 176;
                    break;
                }
                n3 = 176;
                break;
            }
            case -1968506276: {
                if (bl) {
                    if (n2 != -1627316424) break;
                    n3 = 175;
                    break;
                }
                n3 = 175;
                break;
            }
            case -30207860: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 177;
                    break;
                }
                n3 = 177;
                break;
            }
            case 174352: {
                if (bl) {
                    if (n2 != 105060) break;
                    n3 = 173;
                    break;
                }
                n3 = 173;
                break;
            }
            case 4766113: {
                if (bl) {
                    if (n2 != 64712349) break;
                    n3 = 178;
                    break;
                }
                n3 = 178;
                break;
            }
            case 25224473: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 171;
                    break;
                }
                n3 = 171;
                break;
            }
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 170;
                    break;
                }
                n3 = 170;
                break;
            }
            case 654139433: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 172;
                    break;
                }
                n3 = 172;
                break;
            }
            case 1627873078: {
                if (bl) {
                    if (n2 != 64712349) break;
                    n3 = 174;
                    break;
                }
                n3 = 174;
                break;
            }
        }
        return n3;
    }

    private int a33(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 179;
                    break;
                }
                n3 = 179;
                break;
            }
        }
        return n3;
    }

    private int a34(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 730044910: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 181;
                    break;
                }
                n3 = 181;
                break;
            }
            case 730463215: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 180;
                    break;
                }
                n3 = 180;
                break;
            }
            case 1826313106: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 182;
                    break;
                }
                n3 = 182;
                break;
            }
        }
        return n3;
    }

    private int a35(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -55108605: {
                if (bl) {
                    if (n2 != 855937925) break;
                    n3 = 185;
                    break;
                }
                n3 = 185;
                break;
            }
            case 25224473: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 184;
                    break;
                }
                n3 = 184;
                break;
            }
            case 108404676: {
                if (bl) {
                    if (n2 != -1402721757) break;
                    n3 = 183;
                    break;
                }
                n3 = 183;
                break;
            }
        }
        return n3;
    }

    public int getIndex(String string, String string2, Class[] classArray) {
        int n;
        boolean bl;
        int n2 = -1;
        int n3 = RuntimeUtil.buildKey(string);
        int n4 = RuntimeUtil.buildKey(string2);
        if (classArray != null) {
            bl = true;
            n = RuntimeUtil.buildKey(classArray);
        } else {
            bl = false;
            n = 0;
        }
        switch (n3) {
            case -2122741444: {
                n2 = this.a24(n4, bl, n);
                break;
            }
            case -1985293251: {
                n2 = this.a32(n4, bl, n);
                break;
            }
            case -1939384249: {
                n2 = this.a0(n4, bl, n);
                break;
            }
            case -1869555686: {
                n2 = this.a13(n4, bl, n);
                break;
            }
            case -1638994009: {
                n2 = this.a28(n4, bl, n);
                break;
            }
            case -1548736924: {
                n2 = this.a8(n4, bl, n);
                break;
            }
            case -1488642403: {
                n2 = this.a27(n4, bl, n);
                break;
            }
            case -1485179240: {
                n2 = this.a15(n4, bl, n);
                break;
            }
            case -1290023261: {
                n2 = this.a19(n4, bl, n);
                break;
            }
            case -1222912213: {
                n2 = this.a7(n4, bl, n);
                break;
            }
            case -1139439209: {
                n2 = this.a2(n4, bl, n);
                break;
            }
            case -1049699397: {
                n2 = this.a5(n4, bl, n);
                break;
            }
            case -965381897: {
                n2 = this.a9(n4, bl, n);
                break;
            }
            case -784254897: {
                n2 = this.a12(n4, bl, n);
                break;
            }
            case -673026827: {
                n2 = this.a34(n4, bl, n);
                break;
            }
            case -57568228: {
                n2 = this.a17(n4, bl, n);
                break;
            }
            case -26116156: {
                n2 = this.a26(n4, bl, n);
                break;
            }
            case 7467002: {
                n2 = this.a3(n4, bl, n);
                break;
            }
            case 140714148: {
                n2 = this.a18(n4, bl, n);
                break;
            }
            case 286378372: {
                n2 = this.a21(n4, bl, n);
                break;
            }
            case 325540641: {
                n2 = this.a6(n4, bl, n);
                break;
            }
            case 443055968: {
                n2 = this.a29(n4, bl, n);
                break;
            }
            case 631559785: {
                n2 = this.a33(n4, bl, n);
                break;
            }
            case 758467332: {
                n2 = this.a25(n4, bl, n);
                break;
            }
            case 796651089: {
                n2 = this.a35(n4, bl, n);
                break;
            }
            case 926537686: {
                n2 = this.a23(n4, bl, n);
                break;
            }
            case 981481937: {
                n2 = this.a4(n4, bl, n);
                break;
            }
            case 1211341760: {
                n2 = this.a14(n4, bl, n);
                break;
            }
            case 1217094052: {
                n2 = this.a20(n4, bl, n);
                break;
            }
            case 1237779499: {
                n2 = this.a11(n4, bl, n);
                break;
            }
            case 1357249654: {
                n2 = this.a22(n4, bl, n);
                break;
            }
            case 1678918807: {
                n2 = this.a10(n4, bl, n);
                break;
            }
            case 1767198913: {
                n2 = this.a31(n4, bl, n);
                break;
            }
            case 1862702654: {
                n2 = this.a1(n4, bl, n);
                break;
            }
            case 1913326951: {
                n2 = this.a30(n4, bl, n);
                break;
            }
            case 2029893466: {
                n2 = this.a16(n4, bl, n);
                break;
            }
        }
        return n2;
    }

    private Object f0(int n, Object object, Object[] objectArray) throws Throwable {
        switch (n) {
            case 0: {
                return ASLNavigationServiceMainMapFactory.createMainMapService((AbstractTarget)objectArray[0], (int[])objectArray[1]);
            }
            case 1: {
                ((ASLNavigationServiceMainMapTarget)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 2: {
                ((ASLNavigationServiceMainMapTarget)object).clickInMap((Point)objectArray[0]);
                return null;
            }
            case 3: {
                ((ASLNavigationServiceMainMapTarget)object).dragMap((short)((Number)objectArray[0]).intValue(), (short)((Number)objectArray[1]).intValue());
                return null;
            }
            case 4: {
                ((ASLNavigationServiceMainMapTarget)object).dragMapStop();
                return null;
            }
            case 5: {
                ((ASLNavigationServiceMainMapTarget)object).goToLocation((ASLNavigationMapConfiguration)objectArray[0]);
                return null;
            }
            case 6: {
                ((ASLNavigationServiceMainMapTarget)object).goToLocation((ASLNavigationMapConfiguration)objectArray[0], (Boolean)objectArray[1]);
                return null;
            }
            case 7: {
                ((ASLNavigationServiceMainMapTarget)object).lockMapViewer();
                return null;
            }
            case 8: {
                ((ASLNavigationServiceMainMapTarget)object).setTrafficIncidents((Boolean)objectArray[0]);
                return null;
            }
            case 9: {
                ((ASLNavigationServiceMainMapTarget)object).unlockMapViewer();
                return null;
            }
            case 10: {
                ((ASLNavigationServiceMainMapTarget)object).zoomIn();
                return null;
            }
            case 11: {
                ((ASLNavigationServiceMainMapTarget)object).zoomOut();
                return null;
            }
            case 12: {
                ((ASLNavigationServiceMainMapTarget)object).zoomTwoFingers(((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue(), ((Number)objectArray[2]).intValue(), ((Number)objectArray[3]).intValue());
                return null;
            }
            case 13: {
                ((ASLNavigationServiceMainMapTarget)object).zoomTwoFingersStop();
                return null;
            }
            case 14: {
                ((ASLNavigationServiceMainMapTarget)object).setMapSwitchState(((Number)objectArray[0]).intValue());
                return null;
            }
            case 15: {
                return RuntimeUtil.valueOf(((ASLNavigationServiceMainMapTarget)object).getMapSwitchState());
            }
            case 16: {
                return RuntimeUtil.valueOf(((ASLNavigationServiceMainMapTarget)object).getHeadingValue());
            }
            case 17: {
                return RuntimeUtil.valueOf(((ASLNavigationServiceMainMapTarget)object).getMapVisibilityForFPKSwitch());
            }
            case 18: {
                ((ASLNavigationServiceMainMapTarget)object).configureVicsEventNoticeMap(((Number)objectArray[0]).longValue());
                return null;
            }
            case 19: {
                ((ASLNavigationServiceMainMapTarget)object).setGeneralPoiVisibility((Boolean)objectArray[0]);
                return null;
            }
            case 20: {
                ((ASLNavigationServiceMainMapTarget)object).releaseView();
                return null;
            }
            case 21: {
                return RuntimeUtil.valueOf(((ASLNavigationServiceMainMapTarget)object).getICMapServiceState());
            }
            case 22: {
                return RuntimeUtil.valueOf(((ASLNavigationServiceMainMapTarget)object).isMapSwitchFunctionAvailableInKombi());
            }
            case 23: {
                ((ASLNavigationServiceMainMapTarget)object).setMapSwitchFunctionAvailableInKombi((Boolean)objectArray[0]);
                return null;
            }
            case 24: {
                return RuntimeUtil.valueOf(((ASLNavigationServiceMainMapTarget)object).getMainMapZoomLevel());
            }
            case 25: {
                ((ASLNavigationServiceMainMapTarget)object).viewSetVisible();
                return null;
            }
            case 26: {
                ((ASLNavigationServiceMainMapTarget)object).viewSetInvisible();
                return null;
            }
            case 27: {
                ((ASLNavigationServiceMainMapTarget)object).ensureTMCVisibility(((Number)objectArray[0]).longValue());
                return null;
            }
            case 28: {
                ((ASLNavigationServiceMainMapTarget)object).deactivateOverviewZoom();
                return null;
            }
            case 29: {
                return RuntimeUtil.valueOf(((ASLNavigationServiceMainMapTarget)object).getMainMapPerspective());
            }
            case 30: {
                return RuntimeUtil.valueOf(((ASLNavigationServiceMainMapTarget)object).isMapTemporarilyInABT());
            }
            case 31: {
                ((DSIAdbEditTarget)object).reset((HashMap)objectArray[0]);
                return null;
            }
        }
        return null;
    }

    private Object f1(int n, Object object, Object[] objectArray) throws Throwable {
        switch (n) {
            case 32: {
                return ((DSIAdbEditTarget)object).createAdbEdit((AbstractTarget)objectArray[0], (int[])objectArray[1]);
            }
            case 33: {
                ((DSIMapViewerGoogleCtrlTarget)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 34: {
                return ((DSIMapViewerGoogleCtrlTarget)object).createGoogleCtrl((AbstractTarget)objectArray[0], (int[])objectArray[1]);
            }
            case 35: {
                ((GoogleEarthLicenseTargetHSM)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 36: {
                ((GoogleEarthLicenseTargetHSM)object).transStateWork();
                return null;
            }
            case 37: {
                return ((GoogleEarthLicenseTargetHSM)object).getGoogleEarthServiceID();
            }
            case 38: {
                ((GoogleEarthLicenseTargetHSM)object).setGoogleEarthServiceID((String)objectArray[0]);
                return null;
            }
            case 39: {
                return RuntimeUtil.valueOf(((GoogleEarthLicenseTargetHSM)object).isMapViewerReady());
            }
            case 40: {
                ((GoogleEarthLicenseTargetHSM)object).setMapViewerReady((Boolean)objectArray[0]);
                return null;
            }
            case 41: {
                return RuntimeUtil.valueOf(((GoogleEarthLicenseTargetHSM)object).isMapSwitcherReady());
            }
            case 42: {
                ((GoogleEarthLicenseTargetHSM)object).setMapSwitcherReady((Boolean)objectArray[0]);
                return null;
            }
            case 43: {
                return RuntimeUtil.valueOf(((GoogleEarthLicenseTargetHSM)object).isGoogleAvailableInServiceList());
            }
            case 44: {
                ((GoogleEarthLicenseTargetHSM)object).setGoogleAvailableInServiceList((Boolean)objectArray[0]);
                return null;
            }
            case 45: {
                ((DSIMapViewerStreetViewCtrlTarget)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 46: {
                return ((DSIMapViewerStreetViewCtrlTarget)object).createStreetViewCtrl((AbstractTarget)objectArray[0], (int[])objectArray[1]);
            }
            case 47: {
                return ((DSIMapViewerStreetViewCtrlTarget)object).getDatapool();
            }
            case 48: {
                ((DSIMapViewerGetInfoForScreenPositionTargetHSM)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 49: {
                return RuntimeUtil.valueOf(((DSIMapViewerGetInfoForScreenPositionTargetHSM)object).isStateGetInfoInactive());
            }
            case 50: {
                ((DSIMapViewerGetInfoForScreenPositionTargetHSM)object).setMapViewer((DSIMapViewerControl)objectArray[0]);
                return null;
            }
            case 51: {
                ((DSIMapViewerGetInfoForScreenPositionTargetHSM)object).clearQueue();
                return null;
            }
            case 52: {
                ((DSIMapViewerStatusTarget)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 53: {
                ((DSIMapViewerStatusTarget)object).setGeneralPoiVisibility((Boolean)objectArray[0]);
                return null;
            }
            case 54: {
                ((DSIMapViewerStatusTarget)object).setBrandIconStyle((int[])objectArray[0], ((Number)objectArray[1]).intValue());
                return null;
            }
            case 55: {
                ((DSIMapViewerStatusTarget)object).ehSetCategoryVisibility(((Number)objectArray[0]).intValue(), (int[])objectArray[1], (boolean[])objectArray[2]);
                return null;
            }
            case 56: {
                ((DSIMapViewerStatusTarget)object).ehSetCategoryVisibilityToDefault(((Number)objectArray[0]).intValue());
                return null;
            }
            case 57: {
                ((DSIMapViewerStatusTarget)object).dsiMapViewerControlUpdateReady((Boolean)objectArray[0], ((Number)objectArray[1]).intValue());
                return null;
            }
            case 58: {
                return ((DSIMapViewerStatusTarget)object).dsiMapViewerControlUpdateZoomList((float[])objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 59: {
                ((DSIMapViewerControlSwitchMapviewerTargetHSM)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 60: {
                return ((DSIMapViewerControlSwitchMapviewerTargetHSM)object).getDatapool();
            }
            case 61: {
                ((DSIMapViewerControlSwitchMapviewerTargetHSM)object).transStateMain();
                return null;
            }
            case 62: {
                ((DSIMapViewerControlSwitchMapviewerTargetHSM)object).transStateConfigureMapViewerNew();
                return null;
            }
            case 63: {
                ((DSIMapViewerControlSwitchMapviewerTargetHSM)object).transStateGoogleEarthRestart();
                return null;
            }
        }
        return null;
    }

    private Object f2(int n, Object object, Object[] objectArray) throws Throwable {
        switch (n) {
            case 64: {
                ((DSIMapViewerControlSwitchMapviewerTargetHSM)object).transStateGoogleEarthStart();
                return null;
            }
            case 65: {
                ((DSIMapViewerControlSwitchMapviewerTargetHSM)object).transStateGoogleEarthStop();
                return null;
            }
            case 66: {
                ((DSIMapViewerControlSwitchMapviewerTargetHSM)object).transStateSwitchSuspend();
                return null;
            }
            case 67: {
                ((DSIMapViewerControlSwitchMapviewerTargetHSM)object).transStateSwitchWakeup();
                return null;
            }
            case 68: {
                return ((DSIMobilityHorizonTarget)object).createMobilityHorizon((AbstractTarget)objectArray[0], (int[])objectArray[1]);
            }
            case 69: {
                ((DSINavigationTarget)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 70: {
                return ((DSINavigationTarget)object).createNavigation((AbstractTarget)objectArray[0], (int[])objectArray[1]);
            }
            case 71: {
                ((DSIMapViewerZoomEngineTarget)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 72: {
                return ((DSIMapViewerZoomEngineTarget)object).createMapViewerZoomEngine((AbstractTarget)objectArray[0], (int[])objectArray[1]);
            }
            case 73: {
                ((MapViewerKombiTargetHSM)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 74: {
                ((MapViewerKombiTargetHSM)object).transStateMain();
                return null;
            }
            case 75: {
                return RuntimeUtil.valueOf(((MapViewerKombiTargetHSM)object).isStateInvisbileActive());
            }
            case 76: {
                return RuntimeUtil.valueOf(((MapViewerKombiTargetHSM)object).isStateVisbileActive());
            }
            case 77: {
                return RuntimeUtil.valueOf(((MapViewerKombiTargetHSM)object).isStateContinuousZoomActive());
            }
            case 78: {
                return RuntimeUtil.valueOf(((MapViewerKombiTargetHSM)object).rasterizeZoomLevel(((Number)objectArray[0]).floatValue()));
            }
            case 79: {
                ((MapViewerKombiTargetHSM)object).transStateInitMapViewer();
                return null;
            }
            case 80: {
                ((MapViewerKombiTargetHSM)object).transStateInitMapViewerConfigure();
                return null;
            }
            case 81: {
                ((MapViewerKombiTargetHSM)object).transStateInvisible();
                return null;
            }
            case 82: {
                ((MapViewerKombiTargetHSM)object).transStateRestart();
                return null;
            }
            case 83: {
                ((MapViewerKombiTargetHSM)object).transStateSpeechRecognizerActive();
                return null;
            }
            case 84: {
                ((MapViewerKombiTargetHSM)object).transStateVisible();
                return null;
            }
            case 85: {
                ((MapViewerKombiTargetHSM)object).setPerspective2DNorth();
                return null;
            }
            case 86: {
                ((MapViewerKombiTargetHSM)object).setPerspective2DHeading();
                return null;
            }
            case 87: {
                ((MapViewerKombiTargetHSM)object).setPerspective3D();
                return null;
            }
            case 88: {
                ((MapViewerKombiTargetHSM)object).reloadPersistedData();
                return null;
            }
            case 89: {
                ((MapViewerTargetHSM)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 90: {
                ((MapViewerTargetHSM)object).transStateWork();
                return null;
            }
            case 91: {
                ((MapViewerAutoZoomTargetHSM)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 92: {
                ((MapViewerAutoZoomTargetHSM)object).transStateWork();
                return null;
            }
            case 93: {
                ((MapViewerAutoZoomTargetHSM)object).transStateInit();
                return null;
            }
            case 94: {
                ((MapContentChangerTargetHSM)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 95: {
                return RuntimeUtil.valueOf(((MapContentChangerTargetHSM)object).isPerspectiveOverviewType());
            }
        }
        return null;
    }

    private Object f3(int n, Object object, Object[] objectArray) throws Throwable {
        switch (n) {
            case 96: {
                ((GPSInputTargetHSM)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 97: {
                ((GPSInputTargetHSM)object).transStateMain();
                return null;
            }
            case 98: {
                ((GPSInputTargetHSM)object).transStateInit();
                return null;
            }
            case 99: {
                ((GPSInputTargetHSM)object).sendEvMapMainContentGotoLocation(((Number)objectArray[0]).intValue(), (MapConfiguration)objectArray[1]);
                return null;
            }
            case 100: {
                ((GPSInputTargetHSM)object).transStateMoveMapToNewCoordinates();
                return null;
            }
            case 101: {
                ((GPSInputTargetHSM)object).transStateSetClickInMapClicked();
                return null;
            }
            case 102: {
                ((GPSInputTargetHSM)object).transStateSetClickInMapDragged();
                return null;
            }
            case 103: {
                ((GPSInputTargetHSM)object).updateLocationCurrentAndSendEvent((ILocationWrapper)objectArray[0]);
                return null;
            }
            case 104: {
                ((GPSInputTargetHSM)object).updateLocationCurrentByPosInfo((PosInfo[])objectArray[0]);
                return null;
            }
            case 105: {
                ((GPSInputTargetHSM)object).updateWindowValues(((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue(), ((Number)objectArray[2]).intValue(), ((Number)objectArray[3]).intValue());
                return null;
            }
            case 106: {
                ((GPSInputTargetHSM)object).updateXandY((EventGeneric)objectArray[0]);
                return null;
            }
            case 107: {
                ((DualListViewHsmTarget)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 108: {
                ((MapViewerFocusTargetHSM)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 109: {
                ((MapViewerFocusTargetHSM)object).transStateMain();
                return null;
            }
            case 110: {
                ((MapViewerFocusTargetHSM)object).transStateInit();
                return null;
            }
            case 111: {
                return RuntimeUtil.valueOf(((MapViewerFocusTargetHSM)object).isPerspectiveOverviewType());
            }
            case 112: {
                ((MapViewerFocusTargetHSM)object).transStateCCPZoom();
                return null;
            }
            case 113: {
                ((MapViewerFocusTargetHSM)object).transStateSurroundingZoom();
                return null;
            }
            case 114: {
                ((MapViewerFocusTargetHSM)object).zoomByAutozoom();
                return null;
            }
            case 115: {
                ((MapViewerFocusTargetHSM)object).zoomByManualPersistedZoomLevel();
                return null;
            }
            case 116: {
                ((MapViewerFocusTargetHSM)object).zoomByManualOverviewZoomLevel();
                return null;
            }
            case 117: {
                ((MapViewerStreetviewTargetHSM)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 118: {
                ((MapViewerStreetviewTargetHSM)object).transStateMain();
                return null;
            }
            case 119: {
                ((MapViewerStreetviewTargetHSM)object).transStateInit();
                return null;
            }
            case 120: {
                ((MapViewerStreetviewTargetHSM)object).presetZoomLevelAndIndexStreetView();
                return null;
            }
            case 121: {
                ((MapViewerStreetviewTargetHSM)object).streetViewZoomIn();
                return null;
            }
            case 122: {
                ((MapViewerStreetviewTargetHSM)object).streetViewZoomOut();
                return null;
            }
            case 123: {
                ((MapViewerStreetviewTargetHSM)object).transStateStreetView();
                return null;
            }
            case 124: {
                ((MapViewerStreetviewTargetHSM)object).transStateStreetViewInvisible();
                return null;
            }
            case 125: {
                ((MapViewerStreetviewTargetHSM)object).transStateStreetViewTwoFingerZoom();
                return null;
            }
            case 126: {
                ((MapViewerHKNavTargetHSM)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 127: {
                ((MapViewerHKNavTargetHSM)object).transStateMain();
                return null;
            }
        }
        return null;
    }

    private Object f4(int n, Object object, Object[] objectArray) throws Throwable {
        switch (n) {
            case 128: {
                ((MapViewerHKNavTargetHSM)object).transStateInit();
                return null;
            }
            case 129: {
                ((MapViewerMapSwitchTargetHSM)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 130: {
                ((MapViewerMapSwitchTargetHSM)object).transStateWork();
                return null;
            }
            case 131: {
                ((MapViewerMapSwitchTargetHSM)object).transStateInit();
                return null;
            }
            case 132: {
                ((MapViewerMapSwitchTargetHSM)object).transStateAtKombi();
                return null;
            }
            case 133: {
                ((MapViewerMapSwitchTargetHSM)object).transStateAtAbt();
                return null;
            }
            case 134: {
                return ((MapViewerMapSwitchTargetHSM)object).getStateAtKombi();
            }
            case 135: {
                return ((MapViewerMapSwitchTargetHSM)object).getStateAtAbt();
            }
            case 136: {
                ((MapViewerPerspectivesTargetHSM)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 137: {
                ((MapViewerPerspectivesTargetHSM)object).transStateMain();
                return null;
            }
            case 138: {
                ((MapViewerPerspectivesTargetHSM)object).transStateAlternativeRoute();
                return null;
            }
            case 139: {
                ((MapViewerPerspectivesTargetHSM)object).transStateCarUp2D();
                return null;
            }
            case 140: {
                ((MapViewerPerspectivesTargetHSM)object).transStateCarUp3D();
                return null;
            }
            case 141: {
                ((MapViewerPerspectivesTargetHSM)object).transStateCarUpBirdview();
                return null;
            }
            case 142: {
                ((MapViewerPerspectivesTargetHSM)object).transStateCountryOverview();
                return null;
            }
            case 143: {
                ((MapViewerPerspectivesTargetHSM)object).transStateDestinationZoom();
                return null;
            }
            case 144: {
                ((MapViewerPerspectivesTargetHSM)object).transStateFinalDestionationZoom();
                return null;
            }
            case 145: {
                ((MapViewerPerspectivesTargetHSM)object).transStateNorthUp2D();
                return null;
            }
            case 146: {
                ((MapViewerPerspectivesTargetHSM)object).transStateOverviewZoom();
                return null;
            }
            case 147: {
                ((MapViewerPerspectivesTargetHSM)object).transStatePNavView();
                return null;
            }
            case 148: {
                ((MapViewerPerspectivesTargetHSM)object).transStateRangeView();
                return null;
            }
            case 149: {
                ((MapViewerPerspectivesTargetHSM)object).transStateRouteOverview();
                return null;
            }
            case 150: {
                ((MapViewerPerspectivesTargetHSM)object).transStateWayPointOverview();
                return null;
            }
            case 151: {
                ((MapViewerRocketzoomTargetHSM)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 152: {
                ((RubberBandHsmTarget)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 153: {
                ((RubberBandHsmTarget)object).transStateMain();
                return null;
            }
            case 154: {
                ((RubberBandHsmTarget)object).transStatePressed();
                return null;
            }
            case 155: {
                ((RubberBandHsmTarget)object).transStateDragMap();
                return null;
            }
            case 156: {
                ((RubberBandHsmTarget)object).transStateDragRoute();
                return null;
            }
            case 157: {
                ((RubberBandHsmTarget)object).transStateRubberBandActive();
                return null;
            }
            case 158: {
                ((RubberBandHsmTarget)object).transStateRubberBandInactive();
                return null;
            }
            case 159: {
                ((RubberBandHsmTarget)object).transStateCancel();
                return null;
            }
        }
        return null;
    }

    private Object f5(int n, Object object, Object[] objectArray) throws Throwable {
        switch (n) {
            case 160: {
                ((TouchApproachTarget)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 161: {
                ((TouchApproachTarget)object).dsiMapViewerControlAsyncException(((Number)objectArray[0]).intValue(), (String)objectArray[1], ((Number)objectArray[2]).intValue());
                return null;
            }
            case 162: {
                return ((TouchApproachTarget)object).dsiMapViewerControlTouchApproachResult((Boolean)objectArray[0]);
            }
            case 163: {
                ((MapViewerTouchgesturesTargetHSM)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 164: {
                ((MapViewerTouchgesturesTargetHSM)object).sendHMIEventNaviClickedIcon();
                return null;
            }
            case 165: {
                return ((MapViewerTouchgesturesTargetHSM)object).getStateOneFingerClickInMap();
            }
            case 166: {
                ((MapInMapViewerTargetHsm)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 167: {
                return RuntimeUtil.valueOf(((MapInMapViewerTargetHsm)object).isOverviewZoomActive());
            }
            case 168: {
                ((de.vw.mib.asl.internal.navigation.map.mapinmap.main.MapInMapViewerTargetHsm)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 169: {
                return RuntimeUtil.valueOf(((MapInMapViewerPerspectivesTargetHsm)object).isOverviewZoomActive());
            }
            case 170: {
                ((MapSetupTargetHSM)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 171: {
                ((MapSetupTargetHSM)object).reloadPersistedData();
                return null;
            }
            case 172: {
                ((MapSetupTargetHSM)object).addDayNightModeListener();
                return null;
            }
            case 173: {
                ((MapSetupTargetHSM)object).onDayNightModeSensorValueChanged(((Number)objectArray[0]).intValue());
                return null;
            }
            case 174: {
                ((MapSetupTargetHSM)object).changeBrandIconStyle((Boolean)objectArray[0]);
                return null;
            }
            case 175: {
                ((MapSetupTargetHSM)object).handleDayNightMode((EventGeneric)objectArray[0]);
                return null;
            }
            case 176: {
                ((MapSetupTargetHSM)object).changeNightDayViewMode((Boolean)objectArray[0]);
                return null;
            }
            case 177: {
                ((MapSetupTargetHSM)object).removeDayNightModeListener();
                return null;
            }
            case 178: {
                ((MapSetupTargetHSM)object).changePoiVisibility((Boolean)objectArray[0]);
                return null;
            }
            case 179: {
                ((GoogleEarthSetupTargetHSM)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 180: {
                ((MobilityHorizonSetupHsmTarget)object).transStateWork();
                return null;
            }
            case 181: {
                ((MobilityHorizonSetupHsmTarget)object).transStateInit();
                return null;
            }
            case 182: {
                ((MobilityHorizonSetupHsmTarget)object).updateHomeLocation();
                return null;
            }
            case 183: {
                ((TrafficMapSetupHsmTarget)object).reset((HashMap)objectArray[0]);
                return null;
            }
            case 184: {
                ((TrafficMapSetupHsmTarget)object).reloadPersistedData();
                return null;
            }
            case 185: {
                ((TrafficMapSetupHsmTarget)object).forwardValuesToKombi((Boolean)objectArray[0], (Boolean)objectArray[1], (Boolean)objectArray[2]);
                return null;
            }
        }
        return null;
    }

    public Object invoke(int n, Object object, Object[] objectArray) throws InvocationTargetException {
        try {
            switch (n >> 5) {
                case 0: {
                    return this.f0(n, object, objectArray);
                }
                case 1: {
                    return this.f1(n, object, objectArray);
                }
                case 2: {
                    return this.f2(n, object, objectArray);
                }
                case 3: {
                    return this.f3(n, object, objectArray);
                }
                case 4: {
                    return this.f4(n, object, objectArray);
                }
                case 5: {
                    return this.f5(n, object, objectArray);
                }
            }
            return null;
        }
        catch (Throwable throwable) {
            throw new InvocationTargetException(throwable);
        }
    }
}

