/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.reflection.generated.mma;

import de.vw.mib.asl.internal.navigation.caching.IconKey;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdAddChar;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdCancelSpeller;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdDmLastDestinationsDeleteAll;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdDmLastDestinationsGet;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdGetLastCityHistoryEntry;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdGetLastStreetHistoryEntry;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdGetLocationDescriptionTransform;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdGetLocationFromLiValueListElement;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdGetMatchingNVC;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdHistoryAddLocation;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdLastCityHistoryAdd;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdLastStateHistoryAdd;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdLastStreetHistoryAdd;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdLiGetState;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdNavLocationToStream;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdPoiGetXt9LDBs;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdPoiSelectSelectionCriteria;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdPoiStartSpellerAlongRoute;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdPoiStartSpellerAlongRouteAdvanced;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdRequestValueListByListIndex;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdRestoreState;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdRmRouteAdd;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdRmRouteDelete;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdSelectByCategoryUid;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdSelectByMultipleCategoryUids;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdSelectListItem;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdSelectListItemByIdent;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdSelectListItemPoi;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdSetCountryForCityAndStreetHistory;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdSetCurrentLD;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdSetInput;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdSetLiValueListWindowSize;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdSetNVCRange;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdStartSpeller;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdStopSpeller;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdStreamToNavLocation;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdStripLocation;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdTransformAndStrip;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdTransformAndToStream;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdTryBestMatch;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdTryMatchLocation;
import de.vw.mib.asl.internal.navigation.gateway.command.CmdUndoChar;
import de.vw.mib.asl.internal.navigation.map.asl.service.ASLNavigationServiceMainMapStateWork;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.mapviewer.getinfoforscreenposition.DSIMapViewerGetInfoForScreenPositionStateGetInfo;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.mapviewer.getinfoforscreenposition.DSIMapViewerGetInfoForScreenPositionStateMain;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.mapviewer.switchmapviewer.DSIMapViewerControlSwitchMapviewerStateConfigureMapViewerNew;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.mapviewer.switchmapviewer.DSIMapViewerControlSwitchMapviewerStateGoogleEarthRestart;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.mapviewer.switchmapviewer.DSIMapViewerControlSwitchMapviewerStateInit;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.mapviewer.switchmapviewer.DSIMapViewerControlSwitchMapviewerStateMain;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.mapviewer.switchmapviewer.DSIMapViewerControlSwitchMapviewerStateSwitch;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.mapviewer.switchmapviewer.DSIMapViewerControlSwitchMapviewerStateSwitchSuspend;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.mapviewer.switchmapviewer.DSIMapViewerControlSwitchMapviewerStateSwitchWakeup;
import de.vw.mib.asl.internal.navigation.map.kombi.MapViewerKombiStateInit;
import de.vw.mib.asl.internal.navigation.map.kombi.MapViewerKombiStateInitMapViewerConfigure;
import de.vw.mib.asl.internal.navigation.map.kombi.MapViewerKombiStateInvisible;
import de.vw.mib.asl.internal.navigation.map.kombi.MapViewerKombiStateMain;
import de.vw.mib.asl.internal.navigation.map.kombi.MapViewerKombiStateVisible;
import de.vw.mib.asl.internal.navigation.map.mainmap.MapViewerStateMain;
import de.vw.mib.asl.internal.navigation.map.mainmap.autozoom.MapViewerAutoZoomStateWork;
import de.vw.mib.asl.internal.navigation.map.mainmap.destinput.gps.GPSInputStateInit;
import de.vw.mib.asl.internal.navigation.map.mainmap.destinput.gps.GPSInputStateMain;
import de.vw.mib.asl.internal.navigation.map.mainmap.destinput.gps.GPSInputStateMoveMapToNewCoordinates;
import de.vw.mib.asl.internal.navigation.map.mainmap.duallistview.DualListViewStateActive;
import de.vw.mib.asl.internal.navigation.map.mainmap.duallistview.DualListViewStateMapDragged;
import de.vw.mib.asl.internal.navigation.map.mainmap.google.streetview.MapViewerStreetviewStateMain;
import de.vw.mib.asl.internal.navigation.map.mainmap.google.streetview.MapViewerStreetviewStateStreetView;
import de.vw.mib.asl.internal.navigation.map.mainmap.google.streetview.MapViewerStreetviewStateStreetViewInvisible;
import de.vw.mib.asl.internal.navigation.map.mainmap.mapswitch.MapViewerMapSwitchStateAtKombi;
import de.vw.mib.asl.internal.navigation.map.mainmap.perspectives.MapViewerPerspectivesStateCountryOverview;
import de.vw.mib.asl.internal.navigation.map.mainmap.perspectives.MapViewerPerspectivesStateDestinationZoom;
import de.vw.mib.asl.internal.navigation.map.mainmap.perspectives.MapViewerPerspectivesStateFinalDestinationZoom;
import de.vw.mib.asl.internal.navigation.map.mainmap.perspectives.MapViewerPerspectivesStateMain;
import de.vw.mib.asl.internal.navigation.map.mainmap.perspectives.MapViewerPerspectivesStateOverviewZoom;
import de.vw.mib.asl.internal.navigation.map.mainmap.rocketzoom.MapViewerRocketzoomStateActive;
import de.vw.mib.asl.internal.navigation.map.mainmap.rubberband.RubberBandStateActive;
import de.vw.mib.asl.internal.navigation.map.mainmap.rubberband.RubberBandStateCancel;
import de.vw.mib.asl.internal.navigation.map.mainmap.rubberband.RubberbandStateDragRoute;
import de.vw.mib.asl.internal.navigation.map.mainmap.touchgestures.MapViewerTouchgesturesStateOneFingerClickInMap;
import de.vw.mib.asl.internal.navigation.map.mainmap.touchgestures.MapViewerTouchgesturesStateOneFingerClickInMapNew;
import de.vw.mib.asl.internal.navigation.map.mapinmap.MapInMapViewerStateInit;
import de.vw.mib.asl.internal.navigation.map.mapinmap.MapInMapViewerStateMain;
import de.vw.mib.asl.internal.navigation.map.mapinmap.MapInMapViewerStateRestart;
import de.vw.mib.asl.internal.navigation.map.mapinmap.autozoom.MapInMapViewerAutoZoomStateWork;
import de.vw.mib.asl.internal.navigation.map.mapinmap.main.MapInMapViewerStateWork;
import de.vw.mib.asl.internal.navigation.map.mapinmap.perspectives.MapInMapViewerPerspectivesStateInit;
import de.vw.mib.asl.internal.navigation.map.setup.MapSetupStateEarlyMap;
import de.vw.mib.asl.internal.navigation.map.setup.MapSetupStateMain;
import de.vw.mib.asl.internal.navigation.map.setup.google.earth.GoogleEarthSetupStateWork;
import de.vw.mib.asl.internal.navigation.map.setup.mobilityhorizon.MobilityHorizonSetupStateWork;
import de.vw.mib.asl.internal.navigation.map.setup.trafficmap.TrafficMapSetupStateInit;
import de.vw.mib.asl.internal.navigation.map.setup.trafficmap.TrafficMapSetupStateWork;
import de.vw.mib.reflection.MultipleMethodAccessibleObject;
import de.vw.mib.reflection.RuntimeUtil;
import java.lang.reflect.InvocationTargetException;
import org.dsi.ifc.global.NavLocation;
import org.dsi.ifc.global.NavLocationWgs84;
import org.dsi.ifc.global.NavRectangle;
import org.dsi.ifc.global.ResourceLocator;
import org.dsi.ifc.map.LayerProperty;
import org.dsi.ifc.map.PosInfo;
import org.dsi.ifc.navigation.CalculatedRouteListElement;
import org.dsi.ifc.organizer.AdbEntry;

public final class LR2a6a2d34
extends MultipleMethodAccessibleObject {
    private int a0(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a1(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -1742139752: {
                if (bl) {
                    if (n2 != 3890111) break;
                    n3 = 1;
                    break;
                }
                n3 = 1;
                break;
            }
            case -823911215: {
                if (bl) {
                    if (n2 != 1418859852) break;
                    n3 = 4;
                    break;
                }
                n3 = 4;
                break;
            }
            case -540803933: {
                if (bl) {
                    if (n2 != 68598940) break;
                    n3 = 8;
                    break;
                }
                n3 = 8;
                break;
            }
            case -363569082: {
                if (bl) {
                    if (n2 != 68598940) break;
                    n3 = 0;
                    break;
                }
                n3 = 0;
                break;
            }
            case 363915840: {
                if (bl) {
                    if (n2 != 3991651) break;
                    n3 = 9;
                    break;
                }
                n3 = 9;
                break;
            }
            case 763568389: {
                if (bl) {
                    if (n2 != 68598940) break;
                    n3 = 7;
                    break;
                }
                n3 = 7;
                break;
            }
            case 1088139976: {
                if (bl) {
                    if (n2 != -40083968) break;
                    n3 = 2;
                    break;
                }
                n3 = 2;
                break;
            }
            case 1828107028: {
                if (bl) {
                    if (n2 != 101413584) break;
                    n3 = 3;
                    break;
                }
                n3 = 3;
                break;
            }
            case 1859500672: {
                if (bl) {
                    if (n2 != 3890114) break;
                    n3 = 6;
                    break;
                }
                n3 = 6;
                break;
            }
            case 1970393751: {
                if (bl) {
                    if (n2 != 3890114) break;
                    n3 = 5;
                    break;
                }
                n3 = 5;
                break;
            }
        }
        return n3;
    }

    private int a2(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a3(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a4(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -1441590164: {
                if (bl) {
                    if (n2 != -2135789801) break;
                    n3 = 10;
                    break;
                }
                n3 = 10;
                break;
            }
        }
        return n3;
    }

    private int a5(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a6(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a7(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -823911215: {
                if (bl) {
                    if (n2 != 1418859852) break;
                    n3 = 11;
                    break;
                }
                n3 = 11;
                break;
            }
        }
        return n3;
    }

    private int a8(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -540803933: {
                if (bl) {
                    if (n2 != 68598940) break;
                    n3 = 12;
                    break;
                }
                n3 = 12;
                break;
            }
        }
        return n3;
    }

    private int a9(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -363569082: {
                if (bl) {
                    if (n2 != 68598940) break;
                    n3 = 13;
                    break;
                }
                n3 = 13;
                break;
            }
            case 551536138: {
                if (bl) {
                    if (n2 != 3991651) break;
                    n3 = 14;
                    break;
                }
                n3 = 14;
                break;
            }
        }
        return n3;
    }

    private int a10(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a11(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a12(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 551536138: {
                if (bl) {
                    if (n2 != 3991651) break;
                    n3 = 15;
                    break;
                }
                n3 = 15;
                break;
            }
        }
        return n3;
    }

    private int a13(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 1358541925: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 16;
                    break;
                }
                n3 = 16;
                break;
            }
        }
        return n3;
    }

    private int a14(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 407724813: {
                if (bl) {
                    if (n2 != 105060) break;
                    n3 = 18;
                    break;
                }
                n3 = 18;
                break;
            }
            case 551536138: {
                if (bl) {
                    if (n2 != 3991651) break;
                    n3 = 17;
                    break;
                }
                n3 = 17;
                break;
            }
            case 1330838584: {
                if (bl) {
                    if (n2 != 105060) break;
                    n3 = 19;
                    break;
                }
                n3 = 19;
                break;
            }
        }
        return n3;
    }

    private int a15(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 407724813: {
                if (bl) {
                    if (n2 != 105060) break;
                    n3 = 21;
                    break;
                }
                n3 = 21;
                break;
            }
            case 551536138: {
                if (bl) {
                    if (n2 != 3991651) break;
                    n3 = 20;
                    break;
                }
                n3 = 20;
                break;
            }
        }
        return n3;
    }

    private int a16(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 551536138: {
                if (bl) {
                    if (n2 != 3991651) break;
                    n3 = 22;
                    break;
                }
                n3 = 22;
                break;
            }
            case 1330838584: {
                if (bl) {
                    if (n2 != 105060) break;
                    n3 = 23;
                    break;
                }
                n3 = 23;
                break;
            }
        }
        return n3;
    }

    private int a17(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 653013425: {
                if (bl) {
                    if (n2 != 101413584) break;
                    n3 = 24;
                    break;
                }
                n3 = 24;
                break;
            }
        }
        return n3;
    }

    private int a18(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a19(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -540803933: {
                if (bl) {
                    if (n2 != 68598940) break;
                    n3 = 25;
                    break;
                }
                n3 = 25;
                break;
            }
        }
        return n3;
    }

    private int a20(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 1485448752: {
                if (bl) {
                    if (n2 != 68598940) break;
                    n3 = 26;
                    break;
                }
                n3 = 26;
                break;
            }
        }
        return n3;
    }

    private int a21(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 653013425: {
                if (bl) {
                    if (n2 != 101413584) break;
                    n3 = 27;
                    break;
                }
                n3 = 27;
                break;
            }
            case 1358541925: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 28;
                    break;
                }
                n3 = 28;
                break;
            }
        }
        return n3;
    }

    private int a22(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a23(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a24(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a25(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a26(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 1485448752: {
                if (bl) {
                    if (n2 != 68598940) break;
                    n3 = 29;
                    break;
                }
                n3 = 29;
                break;
            }
        }
        return n3;
    }

    private int a27(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a28(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -745517852: {
                if (bl) {
                    if (n2 != 3991651) break;
                    n3 = 33;
                    break;
                }
                n3 = 33;
                break;
            }
            case 300034333: {
                if (bl) {
                    if (n2 != 113300720) break;
                    n3 = 31;
                    break;
                }
                n3 = 31;
                break;
            }
            case 1088139976: {
                if (bl) {
                    if (n2 != -40083968) break;
                    n3 = 30;
                    break;
                }
                n3 = 30;
                break;
            }
            case 1828107028: {
                if (bl) {
                    if (n2 != 101413584) break;
                    n3 = 32;
                    break;
                }
                n3 = 32;
                break;
            }
        }
        return n3;
    }

    private int a29(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a30(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
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
            case 653013425: {
                if (bl) {
                    if (n2 != 101413584) break;
                    n3 = 34;
                    break;
                }
                n3 = 34;
                break;
            }
        }
        return n3;
    }

    private int a33(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a34(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a35(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a36(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a37(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a38(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a39(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a40(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a41(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a42(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a43(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a44(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a45(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a46(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a47(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a48(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a49(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -540803933: {
                if (bl) {
                    if (n2 != 68598940) break;
                    n3 = 36;
                    break;
                }
                n3 = 36;
                break;
            }
            case 1088139976: {
                if (bl) {
                    if (n2 != -40083968) break;
                    n3 = 35;
                    break;
                }
                n3 = 35;
                break;
            }
        }
        return n3;
    }

    private int a50(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -745517852: {
                if (bl) {
                    if (n2 != 3991651) break;
                    n3 = 37;
                    break;
                }
                n3 = 37;
                break;
            }
        }
        return n3;
    }

    private int a51(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 1088139976: {
                if (bl) {
                    if (n2 != -40083968) break;
                    n3 = 38;
                    break;
                }
                n3 = 38;
                break;
            }
        }
        return n3;
    }

    private int a52(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a53(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a54(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 656514783: {
                if (bl) {
                    if (n2 != 3524) break;
                    n3 = 39;
                    break;
                }
                n3 = 39;
                break;
            }
        }
        return n3;
    }

    private int a55(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a56(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a57(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -823911215: {
                if (bl) {
                    if (n2 != 1418859852) break;
                    n3 = 40;
                    break;
                }
                n3 = 40;
                break;
            }
        }
        return n3;
    }

    private int a58(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a59(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a60(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a61(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a62(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a63(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -1197215713: {
                if (bl) {
                    if (n2 != 64712349) break;
                    n3 = 48;
                    break;
                }
                n3 = 48;
                break;
            }
            case 494882206: {
                if (bl) {
                    if (n2 != 3991651) break;
                    n3 = 46;
                    break;
                }
                n3 = 46;
                break;
            }
            case 1088139976: {
                if (bl) {
                    if (n2 != -40083968) break;
                    n3 = 41;
                    break;
                }
                n3 = 41;
                break;
            }
            case 1110901150: {
                if (bl) {
                    if (n2 != 3890111) break;
                    n3 = 45;
                    break;
                }
                n3 = 45;
                break;
            }
            case 1592208974: {
                if (bl) {
                    if (n2 != -40083968) break;
                    n3 = 43;
                    break;
                }
                n3 = 43;
                break;
            }
            case 1870513959: {
                if (bl) {
                    if (n2 != 64712349) break;
                    n3 = 42;
                    break;
                }
                n3 = 42;
                break;
            }
            case 1916002242: {
                if (bl) {
                    if (n2 != 105060) break;
                    n3 = 47;
                    break;
                }
                n3 = 47;
                break;
            }
            case 2004269094: {
                if (bl) {
                    if (n2 != 68598940) break;
                    n3 = 44;
                    break;
                }
                n3 = 44;
                break;
            }
        }
        return n3;
    }

    private int a64(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -1232342779: {
                if (bl) {
                    if (n2 != 3991651) break;
                    n3 = 52;
                    break;
                }
                n3 = 52;
                break;
            }
            case 489517122: {
                if (bl) {
                    if (n2 != 172822152) break;
                    n3 = 53;
                    break;
                }
                n3 = 53;
                break;
            }
            case 804103331: {
                if (bl) {
                    if (n2 != 147795518) break;
                    n3 = 51;
                    break;
                }
                n3 = 51;
                break;
            }
            case 1592208974: {
                if (bl) {
                    if (n2 != -40083968) break;
                    n3 = 50;
                    break;
                }
                n3 = 50;
                break;
            }
            case 1870513959: {
                if (bl) {
                    if (n2 != 64712349) break;
                    n3 = 49;
                    break;
                }
                n3 = 49;
                break;
            }
        }
        return n3;
    }

    private int a65(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 1870513959: {
                if (bl) {
                    if (n2 != 64712349) break;
                    n3 = 54;
                    break;
                }
                n3 = 54;
                break;
            }
        }
        return n3;
    }

    private int a66(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a67(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a68(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a69(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a70(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 25224473: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 55;
                    break;
                }
                n3 = 55;
                break;
            }
            case 1358541925: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 56;
                    break;
                }
                n3 = 56;
                break;
            }
        }
        return n3;
    }

    private int a71(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a72(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a73(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a74(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a75(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a76(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a77(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a78(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -745517852: {
                if (bl) {
                    if (n2 != 3991651) break;
                    n3 = 57;
                    break;
                }
                n3 = 57;
                break;
            }
        }
        return n3;
    }

    private int a79(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 1088139976: {
                if (bl) {
                    if (n2 != -40083968) break;
                    n3 = 58;
                    break;
                }
                n3 = 58;
                break;
            }
        }
        return n3;
    }

    private int a80(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 1088139976: {
                if (bl) {
                    if (n2 != -40083968) break;
                    n3 = 59;
                    break;
                }
                n3 = 59;
                break;
            }
        }
        return n3;
    }

    private int a81(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a82(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -745517852: {
                if (bl) {
                    if (n2 != 3991651) break;
                    n3 = 60;
                    break;
                }
                n3 = 60;
                break;
            }
        }
        return n3;
    }

    private int a83(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a84(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 1088139976: {
                if (bl) {
                    if (n2 != -40083968) break;
                    n3 = 61;
                    break;
                }
                n3 = 61;
                break;
            }
        }
        return n3;
    }

    private int a85(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a86(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a87(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a88(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a89(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -745517852: {
                if (bl) {
                    if (n2 != 3991651) break;
                    n3 = 62;
                    break;
                }
                n3 = 62;
                break;
            }
        }
        return n3;
    }

    private int a90(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a91(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a92(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -1756742986: {
                if (bl) {
                    if (n2 != 1418859852) break;
                    n3 = 65;
                    break;
                }
                n3 = 65;
                break;
            }
            case -992973911: {
                if (bl) {
                    if (n2 != -814410791) break;
                    n3 = 70;
                    break;
                }
                n3 = 70;
                break;
            }
            case -823911215: {
                if (bl) {
                    if (n2 != 1418859852) break;
                    n3 = 63;
                    break;
                }
                n3 = 63;
                break;
            }
            case 614631194: {
                if (bl) {
                    if (n2 != 3991651) break;
                    n3 = 71;
                    break;
                }
                n3 = 71;
                break;
            }
            case 727335687: {
                if (bl) {
                    if (n2 != 68598940) break;
                    n3 = 69;
                    break;
                }
                n3 = 69;
                break;
            }
            case 810628307: {
                if (bl) {
                    if (n2 != 105060) break;
                    n3 = 68;
                    break;
                }
                n3 = 68;
                break;
            }
            case 1466536391: {
                if (bl) {
                    if (n2 != -910090939) break;
                    n3 = 66;
                    break;
                }
                n3 = 66;
                break;
            }
            case 1665850675: {
                if (bl) {
                    if (n2 != -1800777704) break;
                    n3 = 67;
                    break;
                }
                n3 = 67;
                break;
            }
            case 2091589473: {
                if (bl) {
                    if (n2 != -40083968) break;
                    n3 = 64;
                    break;
                }
                n3 = 64;
                break;
            }
        }
        return n3;
    }

    private int a93(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 727335687: {
                if (bl) {
                    if (n2 != 68598940) break;
                    n3 = 72;
                    break;
                }
                n3 = 72;
                break;
            }
        }
        return n3;
    }

    private int a94(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a95(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a96(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a97(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a98(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 1665850675: {
                if (bl) {
                    if (n2 != -1800777704) break;
                    n3 = 73;
                    break;
                }
                n3 = 73;
                break;
            }
        }
        return n3;
    }

    private int a99(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a100(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a101(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a102(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -2074846649: {
                if (bl) {
                    if (n2 != 1665356182) break;
                    n3 = 81;
                    break;
                }
                n3 = 81;
                break;
            }
            case -2016716374: {
                if (bl) {
                    if (n2 != 1790988409) break;
                    n3 = 87;
                    break;
                }
                n3 = 87;
                break;
            }
            case -1966853781: {
                if (bl) {
                    if (n2 != 2014704956) break;
                    n3 = 78;
                    break;
                }
                n3 = 78;
                break;
            }
            case -1807343454: {
                if (bl) {
                    if (n2 != 1489731121) break;
                    n3 = 111;
                    break;
                }
                n3 = 111;
                break;
            }
            case -1740089070: {
                if (bl) {
                    if (n2 != 1684974947) break;
                    n3 = 96;
                    break;
                }
                n3 = 96;
                break;
            }
            case -1738553222: {
                if (bl) {
                    if (n2 != 2018499595) break;
                    n3 = 100;
                    break;
                }
                n3 = 100;
                break;
            }
            case -1536725116: {
                if (bl) {
                    if (n2 != -737631211) break;
                    n3 = 93;
                    break;
                }
                n3 = 93;
                break;
            }
            case -1452548656: {
                if (bl) {
                    if (n2 != -1406570463) break;
                    n3 = 89;
                    break;
                }
                n3 = 89;
                break;
            }
            case -1422773111: {
                if (bl) {
                    if (n2 != -2074579752) break;
                    n3 = 118;
                    break;
                }
                n3 = 118;
                break;
            }
            case -1365561861: {
                if (bl) {
                    if (n2 != -1918268022) break;
                    n3 = 97;
                    break;
                }
                n3 = 97;
                break;
            }
            case -1364744154: {
                if (bl) {
                    if (n2 != -1216426761) break;
                    n3 = 85;
                    break;
                }
                n3 = 85;
                break;
            }
            case -1240726706: {
                if (bl) {
                    if (n2 != -1778641185) break;
                    n3 = 112;
                    break;
                }
                n3 = 112;
                break;
            }
            case -1040213639: {
                if (bl) {
                    if (n2 != 2057555784) break;
                    n3 = 83;
                    break;
                }
                n3 = 83;
                break;
            }
            case -963373045: {
                if (bl) {
                    if (n2 != -1518137510) break;
                    n3 = 106;
                    break;
                }
                n3 = 106;
                break;
            }
            case -792417868: {
                if (bl) {
                    if (n2 != 749153733) break;
                    n3 = 110;
                    break;
                }
                n3 = 110;
                break;
            }
            case -485226831: {
                if (bl) {
                    if (n2 != 19293504) break;
                    n3 = 102;
                    break;
                }
                n3 = 102;
                break;
            }
            case -174669585: {
                if (bl) {
                    if (n2 != -1044572864) break;
                    n3 = 92;
                    break;
                }
                n3 = 92;
                break;
            }
            case -172040872: {
                if (bl) {
                    if (n2 != -1369238745) break;
                    n3 = 114;
                    break;
                }
                n3 = 114;
                break;
            }
            case -123487623: {
                if (bl) {
                    if (n2 != 1418083978) break;
                    n3 = 86;
                    break;
                }
                n3 = 86;
                break;
            }
            case 3642619: {
                if (bl) {
                    if (n2 != 1195260122) break;
                    n3 = 76;
                    break;
                }
                n3 = 76;
                break;
            }
            case 53219281: {
                if (bl) {
                    if (n2 != 35390050) break;
                    n3 = 91;
                    break;
                }
                n3 = 91;
                break;
            }
            case 96785533: {
                if (bl) {
                    if (n2 != 1195260122) break;
                    n3 = 75;
                    break;
                }
                n3 = 75;
                break;
            }
            case 110621626: {
                if (bl) {
                    if (n2 != 1195260122) break;
                    n3 = 77;
                    break;
                }
                n3 = 77;
                break;
            }
            case 144356669: {
                if (bl) {
                    if (n2 != -507449972) break;
                    n3 = 116;
                    break;
                }
                n3 = 116;
                break;
            }
            case 166616976: {
                if (bl) {
                    if (n2 != -386089185) break;
                    n3 = 79;
                    break;
                }
                n3 = 79;
                break;
            }
            case 339753823: {
                if (bl) {
                    if (n2 != -530149456) break;
                    n3 = 80;
                    break;
                }
                n3 = 80;
                break;
            }
            case 384423099: {
                if (bl) {
                    if (n2 != -485480180) break;
                    n3 = 95;
                    break;
                }
                n3 = 95;
                break;
            }
            case 426788875: {
                if (bl) {
                    if (n2 != -698941862) break;
                    n3 = 113;
                    break;
                }
                n3 = 113;
                break;
            }
            case 471265876: {
                if (bl) {
                    if (n2 != 619583269) break;
                    n3 = 94;
                    break;
                }
                n3 = 94;
                break;
            }
            case 480225318: {
                if (bl) {
                    if (n2 != 984745653) break;
                    n3 = 117;
                    break;
                }
                n3 = 117;
                break;
            }
            case 621097709: {
                if (bl) {
                    if (n2 != 1573033406) break;
                    n3 = 109;
                    break;
                }
                n3 = 109;
                break;
            }
            case 853125527: {
                if (bl) {
                    if (n2 != -344072346) break;
                    n3 = 107;
                    break;
                }
                n3 = 107;
                break;
            }
            case 932145625: {
                if (bl) {
                    if (n2 != 573925864) break;
                    n3 = 74;
                    break;
                }
                n3 = 74;
                break;
            }
            case 979084543: {
                if (bl) {
                    if (n2 != 1778178448) break;
                    n3 = 108;
                    break;
                }
                n3 = 108;
                break;
            }
            case 1060925107: {
                if (bl) {
                    if (n2 != 953085378) break;
                    n3 = 105;
                    break;
                }
                n3 = 105;
                break;
            }
            case 1176415189: {
                if (bl) {
                    if (n2 != 72820964) break;
                    n3 = 84;
                    break;
                }
                n3 = 84;
                break;
            }
            case 1435973531: {
                if (bl) {
                    if (n2 != 1940493866) break;
                    n3 = 103;
                    break;
                }
                n3 = 103;
                break;
            }
            case 1517013181: {
                if (bl) {
                    if (n2 != 2021533516) break;
                    n3 = 88;
                    break;
                }
                n3 = 88;
                break;
            }
            case 1570887344: {
                if (bl) {
                    if (n2 != 1083624831) break;
                    n3 = 98;
                    break;
                }
                n3 = 98;
                break;
            }
            case 1598068843: {
                if (bl) {
                    if (n2 != 400870970) break;
                    n3 = 104;
                    break;
                }
                n3 = 104;
                break;
            }
            case 1740808658: {
                if (bl) {
                    if (n2 != 201069859) break;
                    n3 = 101;
                    break;
                }
                n3 = 101;
                break;
            }
            case 1948538395: {
                if (bl) {
                    if (n2 != 822807658) break;
                    n3 = 90;
                    break;
                }
                n3 = 90;
                break;
            }
            case 2051908913: {
                if (bl) {
                    if (n2 != 1054016192) break;
                    n3 = 82;
                    break;
                }
                n3 = 82;
                break;
            }
            case 2055085048: {
                if (bl) {
                    if (n2 != 1403278407) break;
                    n3 = 99;
                    break;
                }
                n3 = 99;
                break;
            }
            case 2068515090: {
                if (bl) {
                    if (n2 != 528776291) break;
                    n3 = 115;
                    break;
                }
                n3 = 115;
                break;
            }
        }
        return n3;
    }

    private int a103(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -2074846649: {
                if (bl) {
                    if (n2 != 1665356182) break;
                    n3 = 128;
                    break;
                }
                n3 = 128;
                break;
            }
            case -2016716374: {
                if (bl) {
                    if (n2 != 1790988409) break;
                    n3 = 134;
                    break;
                }
                n3 = 134;
                break;
            }
            case -1966853781: {
                if (bl) {
                    if (n2 != 2014704956) break;
                    n3 = 125;
                    break;
                }
                n3 = 125;
                break;
            }
            case -1807343454: {
                if (bl) {
                    if (n2 != 1489731121) break;
                    n3 = 158;
                    break;
                }
                n3 = 158;
                break;
            }
            case -1740089070: {
                if (bl) {
                    if (n2 != 1684974947) break;
                    n3 = 143;
                    break;
                }
                n3 = 143;
                break;
            }
            case -1738553222: {
                if (bl) {
                    if (n2 != 2018499595) break;
                    n3 = 147;
                    break;
                }
                n3 = 147;
                break;
            }
            case -1536725116: {
                if (bl) {
                    if (n2 != -737631211) break;
                    n3 = 140;
                    break;
                }
                n3 = 140;
                break;
            }
            case -1452548656: {
                if (bl) {
                    if (n2 != -1406570463) break;
                    n3 = 136;
                    break;
                }
                n3 = 136;
                break;
            }
            case -1422773111: {
                if (bl) {
                    if (n2 != -2074579752) break;
                    n3 = 165;
                    break;
                }
                n3 = 165;
                break;
            }
            case -1365561861: {
                if (bl) {
                    if (n2 != -1918268022) break;
                    n3 = 144;
                    break;
                }
                n3 = 144;
                break;
            }
            case -1364744154: {
                if (bl) {
                    if (n2 != -1216426761) break;
                    n3 = 132;
                    break;
                }
                n3 = 132;
                break;
            }
            case -1240726706: {
                if (bl) {
                    if (n2 != -1778641185) break;
                    n3 = 159;
                    break;
                }
                n3 = 159;
                break;
            }
            case -1077557351: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 120;
                    break;
                }
                n3 = 120;
                break;
            }
            case -1040213639: {
                if (bl) {
                    if (n2 != 2057555784) break;
                    n3 = 130;
                    break;
                }
                n3 = 130;
                break;
            }
            case -963373045: {
                if (bl) {
                    if (n2 != -1518137510) break;
                    n3 = 153;
                    break;
                }
                n3 = 153;
                break;
            }
            case -792417868: {
                if (bl) {
                    if (n2 != 749153733) break;
                    n3 = 157;
                    break;
                }
                n3 = 157;
                break;
            }
            case -485226831: {
                if (bl) {
                    if (n2 != 19293504) break;
                    n3 = 149;
                    break;
                }
                n3 = 149;
                break;
            }
            case -174669585: {
                if (bl) {
                    if (n2 != -1044572864) break;
                    n3 = 139;
                    break;
                }
                n3 = 139;
                break;
            }
            case -172040872: {
                if (bl) {
                    if (n2 != -1369238745) break;
                    n3 = 161;
                    break;
                }
                n3 = 161;
                break;
            }
            case -123487623: {
                if (bl) {
                    if (n2 != 1418083978) break;
                    n3 = 133;
                    break;
                }
                n3 = 133;
                break;
            }
            case 3642619: {
                if (bl) {
                    if (n2 != 1195260122) break;
                    n3 = 123;
                    break;
                }
                n3 = 123;
                break;
            }
            case 53219281: {
                if (bl) {
                    if (n2 != 35390050) break;
                    n3 = 138;
                    break;
                }
                n3 = 138;
                break;
            }
            case 96785533: {
                if (bl) {
                    if (n2 != 1195260122) break;
                    n3 = 122;
                    break;
                }
                n3 = 122;
                break;
            }
            case 110621626: {
                if (bl) {
                    if (n2 != 1195260122) break;
                    n3 = 124;
                    break;
                }
                n3 = 124;
                break;
            }
            case 144356669: {
                if (bl) {
                    if (n2 != -507449972) break;
                    n3 = 163;
                    break;
                }
                n3 = 163;
                break;
            }
            case 166616976: {
                if (bl) {
                    if (n2 != -386089185) break;
                    n3 = 126;
                    break;
                }
                n3 = 126;
                break;
            }
            case 339753823: {
                if (bl) {
                    if (n2 != -530149456) break;
                    n3 = 127;
                    break;
                }
                n3 = 127;
                break;
            }
            case 384423099: {
                if (bl) {
                    if (n2 != -485480180) break;
                    n3 = 142;
                    break;
                }
                n3 = 142;
                break;
            }
            case 426788875: {
                if (bl) {
                    if (n2 != -698941862) break;
                    n3 = 160;
                    break;
                }
                n3 = 160;
                break;
            }
            case 471265876: {
                if (bl) {
                    if (n2 != 619583269) break;
                    n3 = 141;
                    break;
                }
                n3 = 141;
                break;
            }
            case 480225318: {
                if (bl) {
                    if (n2 != 984745653) break;
                    n3 = 164;
                    break;
                }
                n3 = 164;
                break;
            }
            case 621097709: {
                if (bl) {
                    if (n2 != 1573033406) break;
                    n3 = 156;
                    break;
                }
                n3 = 156;
                break;
            }
            case 853125527: {
                if (bl) {
                    if (n2 != -344072346) break;
                    n3 = 154;
                    break;
                }
                n3 = 154;
                break;
            }
            case 932145625: {
                if (bl) {
                    if (n2 != 573925864) break;
                    n3 = 119;
                    break;
                }
                n3 = 119;
                break;
            }
            case 979084543: {
                if (bl) {
                    if (n2 != 1778178448) break;
                    n3 = 155;
                    break;
                }
                n3 = 155;
                break;
            }
            case 1060925107: {
                if (bl) {
                    if (n2 != 953085378) break;
                    n3 = 152;
                    break;
                }
                n3 = 152;
                break;
            }
            case 1176415189: {
                if (bl) {
                    if (n2 != 72820964) break;
                    n3 = 131;
                    break;
                }
                n3 = 131;
                break;
            }
            case 1244919775: {
                if (bl) {
                    if (n2 != -310335607) break;
                    n3 = 121;
                    break;
                }
                n3 = 121;
                break;
            }
            case 1435973531: {
                if (bl) {
                    if (n2 != 1940493866) break;
                    n3 = 150;
                    break;
                }
                n3 = 150;
                break;
            }
            case 1517013181: {
                if (bl) {
                    if (n2 != 2021533516) break;
                    n3 = 135;
                    break;
                }
                n3 = 135;
                break;
            }
            case 1570887344: {
                if (bl) {
                    if (n2 != 1083624831) break;
                    n3 = 145;
                    break;
                }
                n3 = 145;
                break;
            }
            case 1598068843: {
                if (bl) {
                    if (n2 != 400870970) break;
                    n3 = 151;
                    break;
                }
                n3 = 151;
                break;
            }
            case 1740808658: {
                if (bl) {
                    if (n2 != 201069859) break;
                    n3 = 148;
                    break;
                }
                n3 = 148;
                break;
            }
            case 1948538395: {
                if (bl) {
                    if (n2 != 822807658) break;
                    n3 = 137;
                    break;
                }
                n3 = 137;
                break;
            }
            case 2051908913: {
                if (bl) {
                    if (n2 != 1054016192) break;
                    n3 = 129;
                    break;
                }
                n3 = 129;
                break;
            }
            case 2055085048: {
                if (bl) {
                    if (n2 != 1403278407) break;
                    n3 = 146;
                    break;
                }
                n3 = 146;
                break;
            }
            case 2068515090: {
                if (bl) {
                    if (n2 != 528776291) break;
                    n3 = 162;
                    break;
                }
                n3 = 162;
                break;
            }
        }
        return n3;
    }

    private int a104(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a105(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a106(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a107(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a108(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a109(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a110(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a111(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a112(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a113(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -540803933: {
                if (bl) {
                    if (n2 != 68598940) break;
                    n3 = 166;
                    break;
                }
                n3 = 166;
                break;
            }
        }
        return n3;
    }

    private int a114(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -1742047166: {
                if (bl) {
                    if (n2 != 3991651) break;
                    n3 = 170;
                    break;
                }
                n3 = 170;
                break;
            }
            case 300034333: {
                if (bl) {
                    if (n2 != 113300720) break;
                    n3 = 167;
                    break;
                }
                n3 = 167;
                break;
            }
            case 653013425: {
                if (bl) {
                    if (n2 != 101413584) break;
                    n3 = 169;
                    break;
                }
                n3 = 169;
                break;
            }
            case 1828107028: {
                if (bl) {
                    if (n2 != 101413584) break;
                    n3 = 168;
                    break;
                }
                n3 = 168;
                break;
            }
        }
        return n3;
    }

    private int a115(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a116(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a117(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -540803933: {
                if (bl) {
                    if (n2 != 68598940) break;
                    n3 = 171;
                    break;
                }
                n3 = 171;
                break;
            }
        }
        return n3;
    }

    private int a118(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a119(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a120(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 653013425: {
                if (bl) {
                    if (n2 != 101413584) break;
                    n3 = 172;
                    break;
                }
                n3 = 172;
                break;
            }
        }
        return n3;
    }

    private int a121(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a122(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -1742047166: {
                if (bl) {
                    if (n2 != 3991651) break;
                    n3 = 176;
                    break;
                }
                n3 = 176;
                break;
            }
            case 300034333: {
                if (bl) {
                    if (n2 != 113300720) break;
                    n3 = 173;
                    break;
                }
                n3 = 173;
                break;
            }
            case 653013425: {
                if (bl) {
                    if (n2 != 101413584) break;
                    n3 = 175;
                    break;
                }
                n3 = 175;
                break;
            }
            case 1828107028: {
                if (bl) {
                    if (n2 != 101413584) break;
                    n3 = 174;
                    break;
                }
                n3 = 174;
                break;
            }
        }
        return n3;
    }

    private int a123(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a124(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a125(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a126(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -540803933: {
                if (bl) {
                    if (n2 != 68598940) break;
                    n3 = 177;
                    break;
                }
                n3 = 177;
                break;
            }
        }
        return n3;
    }

    private int a127(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a128(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a129(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a130(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a131(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a132(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a133(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -2113062598: {
                if (bl) {
                    if (n2 != 3890114) break;
                    n3 = 179;
                    break;
                }
                n3 = 179;
                break;
            }
            case -540803933: {
                if (bl) {
                    if (n2 != 68598940) break;
                    n3 = 178;
                    break;
                }
                n3 = 178;
                break;
            }
        }
        return n3;
    }

    private int a134(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a135(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -2113062598: {
                if (bl) {
                    if (n2 != 3890114) break;
                    n3 = 183;
                    break;
                }
                n3 = 183;
                break;
            }
            case -1845448794: {
                if (bl) {
                    if (n2 != 3991651) break;
                    n3 = 180;
                    break;
                }
                n3 = 180;
                break;
            }
            case -215985701: {
                if (bl) {
                    if (n2 != 1086231186) break;
                    n3 = 184;
                    break;
                }
                n3 = 184;
                break;
            }
            case 656514783: {
                if (bl) {
                    if (n2 != 3524) break;
                    n3 = 182;
                    break;
                }
                n3 = 182;
                break;
            }
            case 1358541925: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 181;
                    break;
                }
                n3 = 181;
                break;
            }
        }
        return n3;
    }

    private int a136(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a137(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a138(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a139(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case -2135214037: {
                if (bl) {
                    if (n2 != 3991651) break;
                    n3 = 186;
                    break;
                }
                n3 = 186;
                break;
            }
            case 626858335: {
                if (bl) {
                    if (n2 != 20550066) break;
                    n3 = 185;
                    break;
                }
                n3 = 185;
                break;
            }
        }
        return n3;
    }

    private int a140(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a141(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 1358541925: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 187;
                    break;
                }
                n3 = 187;
                break;
            }
            case 1845314727: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 188;
                    break;
                }
                n3 = 188;
                break;
            }
        }
        return n3;
    }

    private int a142(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 1916002242: {
                if (bl) {
                    if (n2 != 105060) break;
                    n3 = 189;
                    break;
                }
                n3 = 189;
                break;
            }
        }
        return n3;
    }

    private int a143(int n, boolean bl, int n2) {
        int n3 = -1;
        int n4 = n;
        return n3;
    }

    private int a144(int n, boolean bl, int n2) {
        int n3 = -1;
        switch (n) {
            case 1358541925: {
                if (bl) {
                    if (n2 != 17) break;
                    n3 = 191;
                    break;
                }
                n3 = 191;
                break;
            }
            case 1916002242: {
                if (bl) {
                    if (n2 != 105060) break;
                    n3 = 190;
                    break;
                }
                n3 = 190;
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
            case -2054867937: {
                n2 = this.a17(n4, bl, n);
                break;
            }
            case -2054761272: {
                n2 = this.a21(n4, bl, n);
                break;
            }
            case -2003122744: {
                n2 = this.a20(n4, bl, n);
                break;
            }
            case -1968406923: {
                n2 = this.a34(n4, bl, n);
                break;
            }
            case -1904256546: {
                n2 = this.a8(n4, bl, n);
                break;
            }
            case -1902073843: {
                n2 = this.a26(n4, bl, n);
                break;
            }
            case -1846436741: {
                n2 = this.a111(n4, bl, n);
                break;
            }
            case -1839941556: {
                n2 = this.a5(n4, bl, n);
                break;
            }
            case -1803481099: {
                n2 = this.a10(n4, bl, n);
                break;
            }
            case -1758618866: {
                n2 = this.a15(n4, bl, n);
                break;
            }
            case -1697451467: {
                n2 = this.a75(n4, bl, n);
                break;
            }
            case -1697451436: {
                n2 = this.a76(n4, bl, n);
                break;
            }
            case -1677956535: {
                n2 = this.a116(n4, bl, n);
                break;
            }
            case -1661044227: {
                n2 = this.a61(n4, bl, n);
                break;
            }
            case -1640809313: {
                n2 = this.a39(n4, bl, n);
                break;
            }
            case -1640805537: {
                n2 = this.a41(n4, bl, n);
                break;
            }
            case -1626149871: {
                n2 = this.a22(n4, bl, n);
                break;
            }
            case -1597400439: {
                n2 = this.a104(n4, bl, n);
                break;
            }
            case -1596747480: {
                n2 = this.a106(n4, bl, n);
                break;
            }
            case -1553780255: {
                n2 = this.a80(n4, bl, n);
                break;
            }
            case -1540209030: {
                n2 = this.a40(n4, bl, n);
                break;
            }
            case -1493503039: {
                n2 = this.a30(n4, bl, n);
                break;
            }
            case -1475633674: {
                n2 = this.a133(n4, bl, n);
                break;
            }
            case -1400499536: {
                n2 = this.a105(n4, bl, n);
                break;
            }
            case -1346798186: {
                n2 = this.a108(n4, bl, n);
                break;
            }
            case -1304165729: {
                n2 = this.a142(n4, bl, n);
                break;
            }
            case -1303747424: {
                n2 = this.a144(n4, bl, n);
                break;
            }
            case -1296729196: {
                n2 = this.a100(n4, bl, n);
                break;
            }
            case -1296622531: {
                n2 = this.a101(n4, bl, n);
                break;
            }
            case -1289830171: {
                n2 = this.a98(n4, bl, n);
                break;
            }
            case -1282468188: {
                n2 = this.a102(n4, bl, n);
                break;
            }
            case -1271310934: {
                n2 = this.a24(n4, bl, n);
                break;
            }
            case -1256873521: {
                n2 = this.a36(n4, bl, n);
                break;
            }
            case -1191677392: {
                n2 = this.a88(n4, bl, n);
                break;
            }
            case -1191366925: {
                n2 = this.a128(n4, bl, n);
                break;
            }
            case -1129898892: {
                n2 = this.a59(n4, bl, n);
                break;
            }
            case -1129792227: {
                n2 = this.a60(n4, bl, n);
                break;
            }
            case -1051573353: {
                n2 = this.a48(n4, bl, n);
                break;
            }
            case -996542678: {
                n2 = this.a143(n4, bl, n);
                break;
            }
            case -984234668: {
                n2 = this.a71(n4, bl, n);
                break;
            }
            case -983816363: {
                n2 = this.a73(n4, bl, n);
                break;
            }
            case -947519886: {
                n2 = this.a97(n4, bl, n);
                break;
            }
            case -945072399: {
                n2 = this.a6(n4, bl, n);
                break;
            }
            case -944965734: {
                n2 = this.a7(n4, bl, n);
                break;
            }
            case -827558096: {
                n2 = this.a121(n4, bl, n);
                break;
            }
            case -827139791: {
                n2 = this.a122(n4, bl, n);
                break;
            }
            case -792093031: {
                n2 = this.a46(n4, bl, n);
                break;
            }
            case -745090039: {
                n2 = this.a47(n4, bl, n);
                break;
            }
            case -727445933: {
                n2 = this.a99(n4, bl, n);
                break;
            }
            case -668024783: {
                n2 = this.a51(n4, bl, n);
                break;
            }
            case -653667913: {
                n2 = this.a16(n4, bl, n);
                break;
            }
            case -643921515: {
                n2 = this.a44(n4, bl, n);
                break;
            }
            case -639598983: {
                n2 = this.a18(n4, bl, n);
                break;
            }
            case -639053255: {
                n2 = this.a137(n4, bl, n);
                break;
            }
            case -638634950: {
                n2 = this.a139(n4, bl, n);
                break;
            }
            case -623272912: {
                n2 = this.a57(n4, bl, n);
                break;
            }
            case -580370389: {
                n2 = this.a64(n4, bl, n);
                break;
            }
            case -514338237: {
                n2 = this.a78(n4, bl, n);
                break;
            }
            case -499799908: {
                n2 = this.a117(n4, bl, n);
                break;
            }
            case -491978114: {
                n2 = this.a0(n4, bl, n);
                break;
            }
            case -491559809: {
                n2 = this.a1(n4, bl, n);
                break;
            }
            case -462734251: {
                n2 = this.a72(n4, bl, n);
                break;
            }
            case -453770810: {
                n2 = this.a69(n4, bl, n);
                break;
            }
            case -371609332: {
                n2 = this.a65(n4, bl, n);
                break;
            }
            case -344075354: {
                n2 = this.a91(n4, bl, n);
                break;
            }
            case -334869952: {
                n2 = this.a92(n4, bl, n);
                break;
            }
            case -309310025: {
                n2 = this.a19(n4, bl, n);
                break;
            }
            case -289131103: {
                n2 = this.a2(n4, bl, n);
                break;
            }
            case -288712798: {
                n2 = this.a3(n4, bl, n);
                break;
            }
            case -279643724: {
                n2 = this.a93(n4, bl, n);
                break;
            }
            case -183408292: {
                n2 = this.a89(n4, bl, n);
                break;
            }
            case -99046912: {
                n2 = this.a123(n4, bl, n);
                break;
            }
            case -59271280: {
                n2 = this.a31(n4, bl, n);
                break;
            }
            case -58852975: {
                n2 = this.a32(n4, bl, n);
                break;
            }
            case -53518988: {
                n2 = this.a67(n4, bl, n);
                break;
            }
            case -53412323: {
                n2 = this.a68(n4, bl, n);
                break;
            }
            case -32371972: {
                n2 = this.a136(n4, bl, n);
                break;
            }
            case 15680533: {
                n2 = this.a79(n4, bl, n);
                break;
            }
            case 21699872: {
                n2 = this.a54(n4, bl, n);
                break;
            }
            case 47033382: {
                n2 = this.a35(n4, bl, n);
                break;
            }
            case 71409034: {
                n2 = this.a96(n4, bl, n);
                break;
            }
            case 86636614: {
                n2 = this.a81(n4, bl, n);
                break;
            }
            case 86743279: {
                n2 = this.a82(n4, bl, n);
                break;
            }
            case 86814153: {
                n2 = this.a85(n4, bl, n);
                break;
            }
            case 175211786: {
                n2 = this.a110(n4, bl, n);
                break;
            }
            case 448761691: {
                n2 = this.a25(n4, bl, n);
                break;
            }
            case 474386381: {
                n2 = this.a45(n4, bl, n);
                break;
            }
            case 642712887: {
                n2 = this.a126(n4, bl, n);
                break;
            }
            case 642819552: {
                n2 = this.a127(n4, bl, n);
                break;
            }
            case 652553191: {
                n2 = this.a132(n4, bl, n);
                break;
            }
            case 674293620: {
                n2 = this.a38(n4, bl, n);
                break;
            }
            case 685033808: {
                n2 = this.a138(n4, bl, n);
                break;
            }
            case 720575010: {
                n2 = this.a9(n4, bl, n);
                break;
            }
            case 745325526: {
                n2 = this.a86(n4, bl, n);
                break;
            }
            case 759280426: {
                n2 = this.a49(n4, bl, n);
                break;
            }
            case 759387091: {
                n2 = this.a50(n4, bl, n);
                break;
            }
            case 766580693: {
                n2 = this.a37(n4, bl, n);
                break;
            }
            case 788456769: {
                n2 = this.a125(n4, bl, n);
                break;
            }
            case 832175913: {
                n2 = this.a58(n4, bl, n);
                break;
            }
            case 878926833: {
                n2 = this.a124(n4, bl, n);
                break;
            }
            case 879429333: {
                n2 = this.a118(n4, bl, n);
                break;
            }
            case 978559612: {
                n2 = this.a53(n4, bl, n);
                break;
            }
            case 1023050904: {
                n2 = this.a14(n4, bl, n);
                break;
            }
            case 1039061005: {
                n2 = this.a134(n4, bl, n);
                break;
            }
            case 1039167670: {
                n2 = this.a135(n4, bl, n);
                break;
            }
            case 1055547489: {
                n2 = this.a77(n4, bl, n);
                break;
            }
            case 1058776389: {
                n2 = this.a55(n4, bl, n);
                break;
            }
            case 1062715467: {
                n2 = this.a112(n4, bl, n);
                break;
            }
            case 1111333037: {
                n2 = this.a4(n4, bl, n);
                break;
            }
            case 1128948780: {
                n2 = this.a23(n4, bl, n);
                break;
            }
            case 1154798570: {
                n2 = this.a27(n4, bl, n);
                break;
            }
            case 1154905235: {
                n2 = this.a28(n4, bl, n);
                break;
            }
            case 1190617085: {
                n2 = this.a115(n4, bl, n);
                break;
            }
            case 1283249624: {
                n2 = this.a94(n4, bl, n);
                break;
            }
            case 1385359223: {
                n2 = this.a119(n4, bl, n);
                break;
            }
            case 1385777528: {
                n2 = this.a120(n4, bl, n);
                break;
            }
            case 1475617332: {
                n2 = this.a12(n4, bl, n);
                break;
            }
            case 1475723997: {
                n2 = this.a13(n4, bl, n);
                break;
            }
            case 1475843548: {
                n2 = this.a29(n4, bl, n);
                break;
            }
            case 1490017563: {
                n2 = this.a52(n4, bl, n);
                break;
            }
            case 1518326401: {
                n2 = this.a90(n4, bl, n);
                break;
            }
            case 1521123651: {
                n2 = this.a140(n4, bl, n);
                break;
            }
            case 1521541956: {
                n2 = this.a141(n4, bl, n);
                break;
            }
            case 1535710829: {
                n2 = this.a113(n4, bl, n);
                break;
            }
            case 1535817494: {
                n2 = this.a114(n4, bl, n);
                break;
            }
            case 1539175016: {
                n2 = this.a42(n4, bl, n);
                break;
            }
            case 1539281681: {
                n2 = this.a43(n4, bl, n);
                break;
            }
            case 1602651887: {
                n2 = this.a107(n4, bl, n);
                break;
            }
            case 1603304846: {
                n2 = this.a109(n4, bl, n);
                break;
            }
            case 1696170943: {
                n2 = this.a33(n4, bl, n);
                break;
            }
            case 1734330995: {
                n2 = this.a62(n4, bl, n);
                break;
            }
            case 1734437660: {
                n2 = this.a63(n4, bl, n);
                break;
            }
            case 1742939545: {
                n2 = this.a11(n4, bl, n);
                break;
            }
            case 1861480211: {
                n2 = this.a129(n4, bl, n);
                break;
            }
            case 1919391003: {
                n2 = this.a130(n4, bl, n);
                break;
            }
            case 1919497668: {
                n2 = this.a131(n4, bl, n);
                break;
            }
            case 1939689254: {
                n2 = this.a83(n4, bl, n);
                break;
            }
            case 1989638543: {
                n2 = this.a66(n4, bl, n);
                break;
            }
            case 1992559205: {
                n2 = this.a95(n4, bl, n);
                break;
            }
            case 2000616806: {
                n2 = this.a103(n4, bl, n);
                break;
            }
            case 2021930851: {
                n2 = this.a70(n4, bl, n);
                break;
            }
            case 2033083170: {
                n2 = this.a84(n4, bl, n);
                break;
            }
            case 2041013686: {
                n2 = this.a87(n4, bl, n);
                break;
            }
            case 2100418642: {
                n2 = this.a74(n4, bl, n);
                break;
            }
            case 2136582250: {
                n2 = this.a56(n4, bl, n);
                break;
            }
        }
        return n2;
    }

    private Object f0(int n, Object object, Object[] objectArray) throws Throwable {
        switch (n) {
            case 0: {
                return ((ASLNavigationServiceMainMapStateWork)object).dsiMapViewerControlUpdateReady((Boolean)objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 1: {
                return ((ASLNavigationServiceMainMapStateWork)object).dsiMapViewerControlUpdateZoomList((float[])objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 2: {
                return ((ASLNavigationServiceMainMapStateWork)object).dsiMapViewerControlUpdateMapPosition((NavLocationWgs84)objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 3: {
                return ((ASLNavigationServiceMainMapStateWork)object).dsiMapViewerControlUpdateZoomLevel(((Number)objectArray[0]).floatValue(), ((Number)objectArray[1]).intValue());
            }
            case 4: {
                ((ASLNavigationServiceMainMapStateWork)object).dsiMapViewerControlAsyncException(((Number)objectArray[0]).intValue(), (String)objectArray[1], ((Number)objectArray[2]).intValue());
                return null;
            }
            case 5: {
                return ((ASLNavigationServiceMainMapStateWork)object).dsiMapViewerControlUpdateMapLayerAvailable((int[])objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 6: {
                return ((ASLNavigationServiceMainMapStateWork)object).dsiMapViewerControlUpdateMapLayerVisible((int[])objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 7: {
                return ((ASLNavigationServiceMainMapStateWork)object).dsiMapViewerControlUpdateSoftZoomRunning((Boolean)objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 8: {
                return ((ASLNavigationServiceMainMapStateWork)object).dsiMapViewerControlUpdateViewFreeze((Boolean)objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 9: {
                return ((ASLNavigationServiceMainMapStateWork)object).dsiNavigationUpdateNavstateOfOperation(((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue());
            }
            case 10: {
                ((DSIMapViewerGetInfoForScreenPositionStateGetInfo)object).dsiMapViewerControlGetInfoForPosition((PosInfo[])objectArray[0]);
                return null;
            }
            case 11: {
                ((DSIMapViewerGetInfoForScreenPositionStateMain)object).dsiMapViewerControlAsyncException(((Number)objectArray[0]).intValue(), (String)objectArray[1], ((Number)objectArray[2]).intValue());
                return null;
            }
            case 12: {
                return ((DSIMapViewerControlSwitchMapviewerStateConfigureMapViewerNew)object).dsiMapViewerControlUpdateViewFreeze((Boolean)objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 13: {
                ((DSIMapViewerControlSwitchMapviewerStateGoogleEarthRestart)object).dsiMapViewerControlUpdateReady((Boolean)objectArray[0], ((Number)objectArray[1]).intValue());
                return null;
            }
            case 14: {
                return ((DSIMapViewerControlSwitchMapviewerStateGoogleEarthRestart)object).dsiMapViewerControlUpdateMapViewerRunLevel(((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue());
            }
            case 15: {
                return ((DSIMapViewerControlSwitchMapviewerStateInit)object).dsiMapViewerControlUpdateMapViewerRunLevel(((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue());
            }
            case 16: {
                ((DSIMapViewerControlSwitchMapviewerStateMain)object).handleNavigationSettingsReset();
                return null;
            }
            case 17: {
                return ((DSIMapViewerControlSwitchMapviewerStateSwitch)object).dsiMapViewerControlUpdateMapViewerRunLevel(((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue());
            }
            case 18: {
                return ((DSIMapViewerControlSwitchMapviewerStateSwitch)object).dsiMapViewerControlSuspendMapViewerResult(((Number)objectArray[0]).intValue());
            }
            case 19: {
                return ((DSIMapViewerControlSwitchMapviewerStateSwitch)object).dsiMapViewerControlWakeupMapViewerResult(((Number)objectArray[0]).intValue());
            }
            case 20: {
                return ((DSIMapViewerControlSwitchMapviewerStateSwitchSuspend)object).dsiMapViewerControlUpdateMapViewerRunLevel(((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue());
            }
            case 21: {
                return ((DSIMapViewerControlSwitchMapviewerStateSwitchSuspend)object).dsiMapViewerControlSuspendMapViewerResult(((Number)objectArray[0]).intValue());
            }
            case 22: {
                return ((DSIMapViewerControlSwitchMapviewerStateSwitchWakeup)object).dsiMapViewerControlUpdateMapViewerRunLevel(((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue());
            }
            case 23: {
                return ((DSIMapViewerControlSwitchMapviewerStateSwitchWakeup)object).dsiMapViewerControlWakeupMapViewerResult(((Number)objectArray[0]).intValue());
            }
            case 24: {
                return ((MapViewerKombiStateInit)object).dsiMapViewerZoomEngineUpdateRecommendedZoom(((Number)objectArray[0]).floatValue(), ((Number)objectArray[1]).intValue());
            }
            case 25: {
                return ((MapViewerKombiStateInitMapViewerConfigure)object).dsiMapViewerControlUpdateViewFreeze((Boolean)objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 26: {
                return ((MapViewerKombiStateInvisible)object).dsiMapViewerControlUpdateViewVisible((Boolean)objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 27: {
                return ((MapViewerKombiStateMain)object).dsiMapViewerZoomEngineUpdateRecommendedZoom(((Number)objectArray[0]).floatValue(), ((Number)objectArray[1]).intValue());
            }
            case 28: {
                ((MapViewerKombiStateMain)object).handleNavigationSettingsReset();
                return null;
            }
            case 29: {
                return ((MapViewerKombiStateVisible)object).dsiMapViewerControlUpdateViewVisible((Boolean)objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 30: {
                return ((MapViewerStateMain)object).dsiMapViewerControlUpdateMapPosition((NavLocationWgs84)objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 31: {
                return ((MapViewerStateMain)object).dsiMapViewerControlUpdateMapRotation((short)((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue());
            }
        }
        return null;
    }

    private Object f1(int n, Object object, Object[] objectArray) throws Throwable {
        switch (n) {
            case 32: {
                return ((MapViewerStateMain)object).dsiMapViewerControlUpdateZoomLevel(((Number)objectArray[0]).floatValue(), ((Number)objectArray[1]).intValue());
            }
            case 33: {
                return ((MapViewerStateMain)object).dsiMapViewerControlUpdateZoomListIndex(((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue());
            }
            case 34: {
                return ((MapViewerAutoZoomStateWork)object).dsiMapViewerZoomEngineUpdateRecommendedZoom(((Number)objectArray[0]).floatValue(), ((Number)objectArray[1]).intValue());
            }
            case 35: {
                return ((GPSInputStateInit)object).dsiMapViewerControlUpdateMapPosition((NavLocationWgs84)objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 36: {
                return ((GPSInputStateInit)object).dsiMapViewerControlUpdateViewFreeze((Boolean)objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 37: {
                return ((GPSInputStateMain)object).dsiMapViewerControlUpdateZoomListIndex(((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue());
            }
            case 38: {
                return ((GPSInputStateMoveMapToNewCoordinates)object).dsiMapViewerControlUpdateMapPosition((NavLocationWgs84)objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 39: {
                return ((DualListViewStateActive)object).dsiMapViewerControlConfigureFlags((long[])objectArray[0]);
            }
            case 40: {
                ((DualListViewStateMapDragged)object).dsiMapViewerControlAsyncException(((Number)objectArray[0]).intValue(), (String)objectArray[1], ((Number)objectArray[2]).intValue());
                return null;
            }
            case 41: {
                return ((MapViewerStreetviewStateMain)object).dsiMapViewerControlUpdateMapPosition((NavLocationWgs84)objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 42: {
                return ((MapViewerStreetviewStateMain)object).dsiMapViewerStreetViewCtrlStreetViewEnabled((Boolean)objectArray[0]);
            }
            case 43: {
                return ((MapViewerStreetviewStateMain)object).dsiMapViewerStreetViewCtrlUpdatePosition((NavLocationWgs84)objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 44: {
                return ((MapViewerStreetviewStateMain)object).dsiMapViewerStreetViewCtrlUpdateStreetViewAvailable((Boolean)objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 45: {
                return ((MapViewerStreetviewStateMain)object).dsiMapViewerStreetViewCtrlUpdateStreetViewZoomList((float[])objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 46: {
                return ((MapViewerStreetviewStateMain)object).dsiMapViewerStreetViewCtrlUpdateStreetViewZoomListIndex(((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue());
            }
            case 47: {
                ((MapViewerStreetviewStateMain)object).updateServiceStatusOnChange(((Number)objectArray[0]).intValue());
                return null;
            }
            case 48: {
                ((MapViewerStreetviewStateMain)object).onDriverDistractionPreventionRequired((Boolean)objectArray[0]);
                return null;
            }
            case 49: {
                return ((MapViewerStreetviewStateStreetView)object).dsiMapViewerStreetViewCtrlStreetViewEnabled((Boolean)objectArray[0]);
            }
            case 50: {
                ((MapViewerStreetviewStateStreetView)object).dsiMapViewerStreetViewCtrlUpdatePosition((NavLocationWgs84)objectArray[0], ((Number)objectArray[1]).intValue());
                return null;
            }
            case 51: {
                return ((MapViewerStreetviewStateStreetView)object).dsiMapViewerStreetViewCtrlUpdateRotation(((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue(), ((Number)objectArray[2]).intValue());
            }
            case 52: {
                return ((MapViewerStreetviewStateStreetView)object).dsiMapViewerStreetViewCtrlUpdateStreetViewLoadStatus(((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue());
            }
            case 53: {
                ((MapViewerStreetviewStateStreetView)object).dsiNavigationLiGetLocationDescriptionTransformResult((NavLocation)objectArray[0]);
                return null;
            }
            case 54: {
                return ((MapViewerStreetviewStateStreetViewInvisible)object).dsiMapViewerStreetViewCtrlStreetViewEnabled((Boolean)objectArray[0]);
            }
            case 55: {
                ((MapViewerMapSwitchStateAtKombi)object).reloadPersistedData();
                return null;
            }
            case 56: {
                ((MapViewerMapSwitchStateAtKombi)object).handleNavigationSettingsReset();
                return null;
            }
            case 57: {
                return ((MapViewerPerspectivesStateCountryOverview)object).dsiMapViewerControlUpdateZoomListIndex(((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue());
            }
            case 58: {
                return ((MapViewerPerspectivesStateDestinationZoom)object).dsiMapViewerControlUpdateMapPosition((NavLocationWgs84)objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 59: {
                return ((MapViewerPerspectivesStateFinalDestinationZoom)object).dsiMapViewerControlUpdateMapPosition((NavLocationWgs84)objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 60: {
                return ((MapViewerPerspectivesStateMain)object).dsiMapViewerControlUpdateZoomListIndex(((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue());
            }
            case 61: {
                return ((MapViewerPerspectivesStateOverviewZoom)object).dsiMapViewerControlUpdateMapPosition((NavLocationWgs84)objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 62: {
                return ((MapViewerRocketzoomStateActive)object).dsiMapViewerControlUpdateZoomListIndex(((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue());
            }
            case 63: {
                return ((RubberBandStateActive)object).dsiMapViewerControlAsyncException(((Number)objectArray[0]).intValue(), (String)objectArray[1], ((Number)objectArray[2]).intValue());
            }
        }
        return null;
    }

    private Object f2(int n, Object object, Object[] objectArray) throws Throwable {
        switch (n) {
            case 64: {
                return ((RubberBandStateActive)object).dsiMapViewerControlUpdateDragRoutePosition((NavLocationWgs84)objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 65: {
                return ((RubberBandStateActive)object).dsiNavigationAsyncException(((Number)objectArray[0]).intValue(), (String)objectArray[1], ((Number)objectArray[2]).intValue());
            }
            case 66: {
                return ((RubberBandStateActive)object).dsiNavigationRgGetRouteBoundingRectangleResult((NavRectangle)objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 67: {
                return ((RubberBandStateActive)object).dsiNavigationRgGetRubberBandPointPositionResult((NavLocationWgs84)objectArray[0], (Boolean)objectArray[1], ((Number)objectArray[2]).intValue());
            }
            case 68: {
                return ((RubberBandStateActive)object).dsiNavigationRgStartRubberbandManipulationResult(((Number)objectArray[0]).intValue());
            }
            case 69: {
                return ((RubberBandStateActive)object).dsiNavigationUpdateRgActive((Boolean)objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 70: {
                return ((RubberBandStateActive)object).dsiNavigationUpdateRgCalculatedRoutes((CalculatedRouteListElement[])objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 71: {
                return ((RubberBandStateActive)object).dsiNavigationUpdateRgRouteCalculationState(((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue());
            }
            case 72: {
                return ((RubberBandStateCancel)object).dsiNavigationUpdateRgActive((Boolean)objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 73: {
                return ((RubberbandStateDragRoute)object).dsiNavigationRgGetRubberBandPointPositionResult((NavLocationWgs84)objectArray[0], (Boolean)objectArray[1], ((Number)objectArray[2]).intValue());
            }
            case 74: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdGetLocationDescriptionTransform((CmdGetLocationDescriptionTransform)objectArray[0]);
                return null;
            }
            case 75: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).error((String)objectArray[0]);
                return null;
            }
            case 76: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).warn((String)objectArray[0]);
                return null;
            }
            case 77: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).trace((String)objectArray[0]);
                return null;
            }
            case 78: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdTryMatchLocation((CmdTryMatchLocation)objectArray[0]);
                return null;
            }
            case 79: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdDmLastDestinationsDeleteAll((CmdDmLastDestinationsDeleteAll)objectArray[0]);
                return null;
            }
            case 80: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdStartSpeller((CmdStartSpeller)objectArray[0]);
                return null;
            }
            case 81: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdPoiStartSpellerAlongRoute((CmdPoiStartSpellerAlongRoute)objectArray[0]);
                return null;
            }
            case 82: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdStopSpeller((CmdStopSpeller)objectArray[0]);
                return null;
            }
            case 83: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdCancelSpeller((CmdCancelSpeller)objectArray[0]);
                return null;
            }
            case 84: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdAddChar((CmdAddChar)objectArray[0]);
                return null;
            }
            case 85: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdUndoChar((CmdUndoChar)objectArray[0]);
                return null;
            }
            case 86: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdSelectListItem((CmdSelectListItem)objectArray[0]);
                return null;
            }
            case 87: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdSelectListItemByIdent((CmdSelectListItemByIdent)objectArray[0]);
                return null;
            }
            case 88: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdSelectByCategoryUid((CmdSelectByCategoryUid)objectArray[0]);
                return null;
            }
            case 89: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdSelectByMultipleCategoryUids((CmdSelectByMultipleCategoryUids)objectArray[0]);
                return null;
            }
            case 90: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdSelectListItemPoi((CmdSelectListItemPoi)objectArray[0]);
                return null;
            }
            case 91: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdPoiSelectSelectionCriteria((CmdPoiSelectSelectionCriteria)objectArray[0]);
                return null;
            }
            case 92: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdRestoreState((CmdRestoreState)objectArray[0]);
                return null;
            }
            case 93: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdLiGetState((CmdLiGetState)objectArray[0]);
                return null;
            }
            case 94: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdSetInput((CmdSetInput)objectArray[0]);
                return null;
            }
            case 95: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdSetCurrentLD((CmdSetCurrentLD)objectArray[0]);
                return null;
            }
        }
        return null;
    }

    private Object f3(int n, Object object, Object[] objectArray) throws Throwable {
        switch (n) {
            case 96: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdTryBestMatch((CmdTryBestMatch)objectArray[0]);
                return null;
            }
            case 97: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdRequestValueListByListIndex((CmdRequestValueListByListIndex)objectArray[0]);
                return null;
            }
            case 98: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdDmLastDestinationsGet((CmdDmLastDestinationsGet)objectArray[0]);
                return null;
            }
            case 99: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdSetCountryForCityAndStreetHistory((CmdSetCountryForCityAndStreetHistory)objectArray[0]);
                return null;
            }
            case 100: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdLastCityHistoryAdd((CmdLastCityHistoryAdd)objectArray[0]);
                return null;
            }
            case 101: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdLastStreetHistoryAdd((CmdLastStreetHistoryAdd)objectArray[0]);
                return null;
            }
            case 102: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdNavLocationToStream((CmdNavLocationToStream)objectArray[0]);
                return null;
            }
            case 103: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdStreamToNavLocation((CmdStreamToNavLocation)objectArray[0]);
                return null;
            }
            case 104: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdStripLocation((CmdStripLocation)objectArray[0]);
                return null;
            }
            case 105: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdGetLastCityHistoryEntry((CmdGetLastCityHistoryEntry)objectArray[0]);
                return null;
            }
            case 106: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdGetLastStreetHistoryEntry((CmdGetLastStreetHistoryEntry)objectArray[0]);
                return null;
            }
            case 107: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdRmRouteDelete((CmdRmRouteDelete)objectArray[0]);
                return null;
            }
            case 108: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdRmRouteAdd((CmdRmRouteAdd)objectArray[0]);
                return null;
            }
            case 109: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdSetLiValueListWindowSize((CmdSetLiValueListWindowSize)objectArray[0]);
                return null;
            }
            case 110: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdGetMatchingNVC((CmdGetMatchingNVC)objectArray[0]);
                return null;
            }
            case 111: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdSetNVCRange((CmdSetNVCRange)objectArray[0]);
                return null;
            }
            case 112: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdHistoryAddLocation((CmdHistoryAddLocation)objectArray[0]);
                return null;
            }
            case 113: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdTransformAndStrip((CmdTransformAndStrip)objectArray[0]);
                return null;
            }
            case 114: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdPoiGetXt9LDBs((CmdPoiGetXt9LDBs)objectArray[0]);
                return null;
            }
            case 115: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdTransformAndToStream((CmdTransformAndToStream)objectArray[0]);
                return null;
            }
            case 116: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdGetLocationFromLiValueListElement((CmdGetLocationFromLiValueListElement)objectArray[0]);
                return null;
            }
            case 117: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdLastStateHistoryAdd((CmdLastStateHistoryAdd)objectArray[0]);
                return null;
            }
            case 118: {
                ((MapViewerTouchgesturesStateOneFingerClickInMap)object).handleCommandCmdPoiStartSpellerAlongRouteAdvanced((CmdPoiStartSpellerAlongRouteAdvanced)objectArray[0]);
                return null;
            }
            case 119: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdGetLocationDescriptionTransform((CmdGetLocationDescriptionTransform)objectArray[0]);
                return null;
            }
            case 120: {
                return ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).getDefaultIcon();
            }
            case 121: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleIconCacheUpdate((IconKey)objectArray[0], (ResourceLocator)objectArray[1], objectArray[2]);
                return null;
            }
            case 122: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).error((String)objectArray[0]);
                return null;
            }
            case 123: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).warn((String)objectArray[0]);
                return null;
            }
            case 124: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).trace((String)objectArray[0]);
                return null;
            }
            case 125: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdTryMatchLocation((CmdTryMatchLocation)objectArray[0]);
                return null;
            }
            case 126: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdDmLastDestinationsDeleteAll((CmdDmLastDestinationsDeleteAll)objectArray[0]);
                return null;
            }
            case 127: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdStartSpeller((CmdStartSpeller)objectArray[0]);
                return null;
            }
        }
        return null;
    }

    private Object f4(int n, Object object, Object[] objectArray) throws Throwable {
        switch (n) {
            case 128: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdPoiStartSpellerAlongRoute((CmdPoiStartSpellerAlongRoute)objectArray[0]);
                return null;
            }
            case 129: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdStopSpeller((CmdStopSpeller)objectArray[0]);
                return null;
            }
            case 130: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdCancelSpeller((CmdCancelSpeller)objectArray[0]);
                return null;
            }
            case 131: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdAddChar((CmdAddChar)objectArray[0]);
                return null;
            }
            case 132: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdUndoChar((CmdUndoChar)objectArray[0]);
                return null;
            }
            case 133: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdSelectListItem((CmdSelectListItem)objectArray[0]);
                return null;
            }
            case 134: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdSelectListItemByIdent((CmdSelectListItemByIdent)objectArray[0]);
                return null;
            }
            case 135: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdSelectByCategoryUid((CmdSelectByCategoryUid)objectArray[0]);
                return null;
            }
            case 136: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdSelectByMultipleCategoryUids((CmdSelectByMultipleCategoryUids)objectArray[0]);
                return null;
            }
            case 137: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdSelectListItemPoi((CmdSelectListItemPoi)objectArray[0]);
                return null;
            }
            case 138: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdPoiSelectSelectionCriteria((CmdPoiSelectSelectionCriteria)objectArray[0]);
                return null;
            }
            case 139: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdRestoreState((CmdRestoreState)objectArray[0]);
                return null;
            }
            case 140: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdLiGetState((CmdLiGetState)objectArray[0]);
                return null;
            }
            case 141: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdSetInput((CmdSetInput)objectArray[0]);
                return null;
            }
            case 142: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdSetCurrentLD((CmdSetCurrentLD)objectArray[0]);
                return null;
            }
            case 143: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdTryBestMatch((CmdTryBestMatch)objectArray[0]);
                return null;
            }
            case 144: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdRequestValueListByListIndex((CmdRequestValueListByListIndex)objectArray[0]);
                return null;
            }
            case 145: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdDmLastDestinationsGet((CmdDmLastDestinationsGet)objectArray[0]);
                return null;
            }
            case 146: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdSetCountryForCityAndStreetHistory((CmdSetCountryForCityAndStreetHistory)objectArray[0]);
                return null;
            }
            case 147: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdLastCityHistoryAdd((CmdLastCityHistoryAdd)objectArray[0]);
                return null;
            }
            case 148: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdLastStreetHistoryAdd((CmdLastStreetHistoryAdd)objectArray[0]);
                return null;
            }
            case 149: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdNavLocationToStream((CmdNavLocationToStream)objectArray[0]);
                return null;
            }
            case 150: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdStreamToNavLocation((CmdStreamToNavLocation)objectArray[0]);
                return null;
            }
            case 151: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdStripLocation((CmdStripLocation)objectArray[0]);
                return null;
            }
            case 152: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdGetLastCityHistoryEntry((CmdGetLastCityHistoryEntry)objectArray[0]);
                return null;
            }
            case 153: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdGetLastStreetHistoryEntry((CmdGetLastStreetHistoryEntry)objectArray[0]);
                return null;
            }
            case 154: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdRmRouteDelete((CmdRmRouteDelete)objectArray[0]);
                return null;
            }
            case 155: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdRmRouteAdd((CmdRmRouteAdd)objectArray[0]);
                return null;
            }
            case 156: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdSetLiValueListWindowSize((CmdSetLiValueListWindowSize)objectArray[0]);
                return null;
            }
            case 157: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdGetMatchingNVC((CmdGetMatchingNVC)objectArray[0]);
                return null;
            }
            case 158: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdSetNVCRange((CmdSetNVCRange)objectArray[0]);
                return null;
            }
            case 159: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdHistoryAddLocation((CmdHistoryAddLocation)objectArray[0]);
                return null;
            }
        }
        return null;
    }

    private Object f5(int n, Object object, Object[] objectArray) throws Throwable {
        switch (n) {
            case 160: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdTransformAndStrip((CmdTransformAndStrip)objectArray[0]);
                return null;
            }
            case 161: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdPoiGetXt9LDBs((CmdPoiGetXt9LDBs)objectArray[0]);
                return null;
            }
            case 162: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdTransformAndToStream((CmdTransformAndToStream)objectArray[0]);
                return null;
            }
            case 163: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdGetLocationFromLiValueListElement((CmdGetLocationFromLiValueListElement)objectArray[0]);
                return null;
            }
            case 164: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdLastStateHistoryAdd((CmdLastStateHistoryAdd)objectArray[0]);
                return null;
            }
            case 165: {
                ((MapViewerTouchgesturesStateOneFingerClickInMapNew)object).handleCommandCmdPoiStartSpellerAlongRouteAdvanced((CmdPoiStartSpellerAlongRouteAdvanced)objectArray[0]);
                return null;
            }
            case 166: {
                ((MapInMapViewerStateInit)object).dsiMapViewerControlUpdateViewFreeze((Boolean)objectArray[0], ((Number)objectArray[1]).intValue());
                return null;
            }
            case 167: {
                return ((MapInMapViewerStateMain)object).dsiMapViewerControlUpdateMapRotation((short)((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue());
            }
            case 168: {
                return ((MapInMapViewerStateMain)object).dsiMapViewerControlUpdateZoomLevel(((Number)objectArray[0]).floatValue(), ((Number)objectArray[1]).intValue());
            }
            case 169: {
                return ((MapInMapViewerStateMain)object).dsiMapViewerZoomEngineUpdateRecommendedZoom(((Number)objectArray[0]).floatValue(), ((Number)objectArray[1]).intValue());
            }
            case 170: {
                return ((MapInMapViewerStateMain)object).dsiMapViewerControlUpdateMapMode(((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue());
            }
            case 171: {
                ((MapInMapViewerStateRestart)object).dsiMapViewerControlUpdateViewFreeze((Boolean)objectArray[0], ((Number)objectArray[1]).intValue());
                return null;
            }
            case 172: {
                return ((MapInMapViewerAutoZoomStateWork)object).dsiMapViewerZoomEngineUpdateRecommendedZoom(((Number)objectArray[0]).floatValue(), ((Number)objectArray[1]).intValue());
            }
            case 173: {
                return ((MapInMapViewerStateWork)object).dsiMapViewerControlUpdateMapRotation((short)((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue());
            }
            case 174: {
                return ((MapInMapViewerStateWork)object).dsiMapViewerControlUpdateZoomLevel(((Number)objectArray[0]).floatValue(), ((Number)objectArray[1]).intValue());
            }
            case 175: {
                return ((MapInMapViewerStateWork)object).dsiMapViewerZoomEngineUpdateRecommendedZoom(((Number)objectArray[0]).floatValue(), ((Number)objectArray[1]).intValue());
            }
            case 176: {
                return ((MapInMapViewerStateWork)object).dsiMapViewerControlUpdateMapMode(((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue());
            }
            case 177: {
                ((MapInMapViewerPerspectivesStateInit)object).dsiMapViewerControlUpdateViewFreeze((Boolean)objectArray[0], ((Number)objectArray[1]).intValue());
                return null;
            }
            case 178: {
                ((MapSetupStateEarlyMap)object).dsiMapViewerControlUpdateViewFreeze((Boolean)objectArray[0], ((Number)objectArray[1]).intValue());
                return null;
            }
            case 179: {
                return ((MapSetupStateEarlyMap)object).dsiMapViewerControlUpdateEhCategoryVisibility((int[])objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 180: {
                ((MapSetupStateMain)object).onUnitChanged(((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue());
                return null;
            }
            case 181: {
                ((MapSetupStateMain)object).handleNavigationSettingsReset();
                return null;
            }
            case 182: {
                return ((MapSetupStateMain)object).dsiMapViewerControlConfigureFlags((long[])objectArray[0]);
            }
            case 183: {
                return ((MapSetupStateMain)object).dsiMapViewerControlUpdateEhCategoryVisibility((int[])objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 184: {
                return ((MapSetupStateMain)object).dsiAdbEditGetEntriesResult(((Number)objectArray[0]).intValue(), (AdbEntry[])objectArray[1]);
            }
            case 185: {
                return ((GoogleEarthSetupStateWork)object).dsiMapViewerGoogleCtrlUpdateAvailableLayers((LayerProperty[])objectArray[0], ((Number)objectArray[1]).intValue());
            }
            case 186: {
                return ((GoogleEarthSetupStateWork)object).dsiMapViewerGoogleCtrlUpdateGoogleDataStatus(((Number)objectArray[0]).intValue(), ((Number)objectArray[1]).intValue());
            }
            case 187: {
                ((MobilityHorizonSetupStateWork)object).handleNavigationSettingsReset();
                return null;
            }
            case 188: {
                ((MobilityHorizonSetupStateWork)object).handleFullFacotryReset();
                return null;
            }
            case 189: {
                ((TrafficMapSetupStateInit)object).updateServiceStatusOnChange(((Number)objectArray[0]).intValue());
                return null;
            }
            case 190: {
                ((TrafficMapSetupStateWork)object).updateServiceStatusOnChange(((Number)objectArray[0]).intValue());
                return null;
            }
            case 191: {
                ((TrafficMapSetupStateWork)object).handleNavigationSettingsReset();
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

