/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.api.impl;

import de.vw.mib.asl.api.navigation.ASLNavigationEventFactory;
import de.vw.mib.asl.api.navigation.NavigationConfiguration;
import de.vw.mib.asl.api.navigation.NavigationDefinitions;
import de.vw.mib.asl.api.navigation.map.ASLNavigationMapAPI;
import de.vw.mib.asl.api.navigation.map.ASLNavigationMapFactory;
import de.vw.mib.asl.api.navigation.map.ASLNavigationServiceMainMap;
import de.vw.mib.asl.api.navigation.map.MapConfiguration;
import de.vw.mib.asl.api.navigation.map.TrafficDualListViewConfiguration;
import de.vw.mib.asl.api.navigation.startup.ASLNavigationContainer;
import de.vw.mib.asl.api.navigation.startup.ASLNavigationStartupFactory;
import de.vw.mib.asl.api.navigation.traffic.TrafficMessageDetails;
import de.vw.mib.asl.api.navigation.util.ASLNavigationUtilFactory;
import de.vw.mib.asl.api.navigation.util.IExtLogger;
import de.vw.mib.asl.framework.api.diagnosis.ASLDiagnosisFactory;
import de.vw.mib.asl.framework.internal.framework.ServiceManager;
import de.vw.mib.asl.internal.navigation.map.GoogleEarthUtils;
import de.vw.mib.asl.internal.navigation.map.api.impl.listeners.FunctionBlockResponseImpl;
import de.vw.mib.asl.internal.navigation.map.asl.service.ASLNavigationServiceMainMapDatapool;
import de.vw.mib.asl.internal.navigation.map.asl.service.ASLNavigationServiceMainMapEvents;
import de.vw.mib.asl.internal.navigation.map.asl.service.ASLNavigationServiceMainMapFactory;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.DSIAdbEditFactoryVW;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.DSIMapViewerControlFactoryVW;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.DSIMapViewerGoogleCtrlFactoryVW;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.DSIMapViewerStreetViewCtrlFactoryVW;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.DSIMapViewerZoomEngineFactoryVW;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.DSIMobilityHorizonVWFactory;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.DSINavigationFactoryVW;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.google.license.GoogleEarthLicenseTargetHSM;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.mapviewer.status.DSIMapViewerStatusTarget;
import de.vw.mib.asl.internal.navigation.map.kombi.MapViewerKombiTargetHSM;
import de.vw.mib.asl.internal.navigation.map.mainmap.MapViewerDatapoolShared;
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
import de.vw.mib.asl.internal.navigation.map.setup.MapSetupTargetHSM;
import de.vw.mib.asl.internal.navigation.map.setup.PersistedMapSetup;
import de.vw.mib.asl.internal.navigation.map.setup.google.earth.GoogleEarthSetupTargetHSM;
import de.vw.mib.asl.internal.navigation.map.setup.mobilityhorizon.MobilityHorizonSetupHsmTarget;
import de.vw.mib.asl.internal.navigation.map.setup.trafficmap.TrafficMapSetupHsmTarget;
import de.vw.mib.genericevents.AbstractTarget;
import de.vw.mib.genericevents.EventGeneric;
import de.vw.mib.genericevents.GenericEvents;
import de.vw.mib.log4mib.LogMessage;
import org.dsi.ifc.global.NavLocation;
import org.dsi.ifc.global.NavLocationWgs84;
import org.dsi.ifc.map.Point;
import org.dsi.ifc.map.PosInfo;
import org.dsi.ifc.organizer.AdbEntry;

public class ASLNavigationMapAPIImpl
implements ASLNavigationMapAPI,
ASLNavigationContainer {
    private IExtLogger LOGGER = null;

    public ASLNavigationMapAPIImpl() {
        ASLNavigationStartupFactory.getNavigationStartupApi().registerContainer(this);
    }

    public void createTargets() throws Exception {
        GenericEvents genericEvents = ServiceManager.eventMain;
        String string = "hsmtask";
        ASLDiagnosisFactory.getDiagnosisApi().getAdaptionApi().requestHmiFuncBlockTbl(new FunctionBlockResponseImpl(ASLNavigationUtilFactory.getNavigationUtilApi().getExtLogger(65536, "[FunctionBlockResponseImpl]"), MapViewerDatapoolShared.getInstance()));
        DSIMapViewerControlFactoryVW.initFactory();
        DSIMapViewerGoogleCtrlFactoryVW.initFactory();
        DSIMapViewerZoomEngineFactoryVW.initFactory();
        DSIAdbEditFactoryVW.initFactory();
        DSINavigationFactoryVW.initFactory();
        DSIMapViewerStreetViewCtrlFactoryVW.initFactory();
        DSIMobilityHorizonVWFactory.initFactory();
        DSIMapViewerStatusTarget[] dSIMapViewerStatusTargetArray = DSIMapViewerControlFactoryVW.getInstance().getMapViewerStatusTargets();
        for (int i = 0; i < dSIMapViewerStatusTargetArray.length; ++i) {
            ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, dSIMapViewerStatusTargetArray[i]);
        }
        ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, DSIMapViewerZoomEngineFactoryVW.getDSIMapViewerZoomEngineFactoryVW());
        ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, DSIAdbEditFactoryVW.getDSIAdbEditFactoryVW());
        ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, DSINavigationFactoryVW.getDSINavigationFactoryVW());
        ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, new ASLNavigationServiceMainMapFactory(genericEvents, 0x144BBB, string));
        ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, new MapContentChangerTargetHSM(genericEvents, 1330017, string));
        ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, new MapViewerTargetHSM(genericEvents, 1330031, string));
        ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, new MapViewerPerspectivesTargetHSM(genericEvents, 1330075, string));
        ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, new MapViewerAutoZoomTargetHSM(genericEvents, 1330076, string));
        ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, new MapViewerRocketzoomTargetHSM(genericEvents, 1330117, string));
        ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, new MapViewerFocusTargetHSM(genericEvents, 1330077, string));
        ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, new MapViewerTouchgesturesTargetHSM(genericEvents, 1330080, string));
        ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, DSIMapViewerStreetViewCtrlFactoryVW.getGoolgeStreetViewStatusTarget());
        ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, DSIMapViewerGoogleCtrlFactoryVW.getGoogleEarthViewStatusTarget());
        ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, DSIMapViewerControlFactoryVW.getTargetMapViewerSwitchMain());
        if (ServiceManager.configManagerDiag.isFeatureFlagSet(187)) {
            ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, new GoogleEarthLicenseTargetHSM(genericEvents, 1330078, string));
            ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, new GoogleEarthSetupTargetHSM(genericEvents, 1330094, string));
        }
        if (ServiceManager.configManagerDiag.isFeatureFlagSet(188)) {
            ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, new MapViewerStreetviewTargetHSM(genericEvents, 1330079, string));
        }
        ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, new MapViewerKombiTargetHSM(ServiceManager.eventMain, 1330083, "hsmtask"));
        if (ServiceManager.configManagerDiag.isFeatureFlagSet(139)) {
            ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, new MapViewerMapSwitchTargetHSM(genericEvents, 1330128, string));
        }
        ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, new GPSInputTargetHSM(genericEvents, 1330064, string));
        if (ServiceManager.configManagerDiag.isFeatureFlagSet(163)) {
            ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, new MapInMapViewerTargetHsm(genericEvents, 1330054, string));
        }
        ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, new MobilityHorizonSetupHsmTarget(genericEvents, 1330004, string));
        ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, new RubberBandHsmTarget(genericEvents, 1330095, string));
        ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, new MapViewerHKNavTargetHSM(genericEvents, 1330106, string));
        ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, new TrafficMapSetupHsmTarget(genericEvents, 1330006, string));
        if (ServiceManager.configManagerDiag.isFeatureFlagSet(121) || ServiceManager.configManagerDiag.isFeatureFlagSet(153)) {
            ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, new DualListViewHsmTarget(genericEvents, 1330081, string));
        }
        if (NavigationConfiguration.TOUCH_APPROACH_IN_MAP_FEATURE_AVAILABLE) {
            ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(3, new TouchApproachTarget(genericEvents, 1330062, string));
        } else if (NavigationDefinitions.NAVI_LOGGER.isTraceEnabled(16384)) {
            LogMessage logMessage = NavigationDefinitions.NAVI_LOGGER.trace(16384);
            logMessage.append("NAVI-STARTUP: ASL_NAVI_TOUCH_APPROACH target not started, because feature flag is disabled.");
            logMessage.log();
        }
        ASLNavigationStartupFactory.getNavigationStartupApi().addTarget(1, new MapSetupTargetHSM(genericEvents, 1330014, string));
    }

    public boolean isGoogleEarthActive() {
        return GoogleEarthUtils.isGoogleEarthActive();
    }

    public boolean isSplitScreenGuidance() {
        return PersistedMapSetup.getInstance().isSplitScreenGuidance();
    }

    public void setSplitScreenGuidance(boolean bl) {
        PersistedMapSetup.getInstance().setSplitScreenGuidance(bl);
    }

    public boolean isSplitScreenNoGuidance() {
        return PersistedMapSetup.getInstance().isSplitScreenNoGuidance();
    }

    public void setSplitScreenNoGuidance(boolean bl) {
        PersistedMapSetup.getInstance().setSplitScreenNoGuidance(bl);
    }

    public int getSplitScreenContentGuidance() {
        return PersistedMapSetup.getInstance().getSplitScreenContentGuidance();
    }

    public void setSplitScreenContentGuidance(int n) {
        PersistedMapSetup.getInstance().setSplitScreenContentGuidance(n);
    }

    public int getSplitScreenContentNoGuidance() {
        return PersistedMapSetup.getInstance().getSplitScreenContentNoGuidance();
    }

    public void setSplitScreenContentNoGuidance(int n) {
        PersistedMapSetup.getInstance().setSplitScreenContentNoGuidance(n);
    }

    public void preRegisterServices() {
        ASLNavigationServiceMainMapEvents.preRegisterServices();
    }

    public ASLNavigationServiceMainMap createMainMapService(AbstractTarget abstractTarget, int[] nArray) {
        return ASLNavigationServiceMainMapFactory.createMainMapService(abstractTarget, nArray);
    }

    public void sendEvAddressBookEntryChanged(AbstractTarget abstractTarget, AdbEntry adbEntry) {
        this.getLOGGER().trace("sendEvAddressBookEntryChanged()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499032);
        eventGeneric.setObject(0, adbEntry);
        ASLNavigationEventFactory.sendEventToTarget(abstractTarget.getTargetId(), 1330014, eventGeneric);
    }

    public void sendEvDestInputHomeLocationChanged() {
        this.getLOGGER().trace("sendEvDestInputHomeLocationChanged()");
        ASLNavigationEventFactory.sendEventToAllObservers(ASLNavigationEventFactory.createEvent(3499003));
    }

    public void sendEvLicenseValidChangedGoogleEarth(boolean bl) {
        this.getLOGGER().trace("sendEvLicenseValidChangedGoogleEarth()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499053);
        eventGeneric.setBoolean(0, bl);
        ASLNavigationEventFactory.sendEventToService(eventGeneric);
    }

    public void sendEvListViewStartScroll() {
        this.getLOGGER().trace("sendEvListViewStartScroll()");
        ASLNavigationEventFactory.sendEventToService(ASLNavigationEventFactory.createEvent(3499006));
    }

    public void sendEvListViewUpdate(NavLocation[] navLocationArray, int n) {
        this.getLOGGER().trace("sendEvListViewUpdate()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499005);
        eventGeneric.setObject(0, navLocationArray);
        eventGeneric.setInt(1, n);
        ASLNavigationEventFactory.sendEventToService(eventGeneric);
    }

    public void sendEvMapInstanceGoogleNotReady() {
        this.getLOGGER().trace("sendEvMapInstanceGoogleNotReady()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499019);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapShowTMCDualList(TrafficDualListViewConfiguration trafficDualListViewConfiguration) {
        this.getLOGGER().trace("sendEvShowTrafficList()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499069);
        eventGeneric.setObject(0, trafficDualListViewConfiguration);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapInstanceGoogleReady() {
        this.getLOGGER().trace("sendEvMapInstanceGoogleReady()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499018);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapInstanceKombiNotReady() {
        this.getLOGGER().trace("sendEvMapInstanceKombiNotReady()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499013);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapInstanceKombiReady() {
        this.getLOGGER().trace("sendEvMapInstanceKombiReady()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499012);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapInstanceMainNotReady() {
        this.getLOGGER().trace("sendEvMapInstanceMainNotReady()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499015);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapInstanceMainNotReadyToNavStartupTarget() {
        this.getLOGGER().trace("sendEvMapInstanceMainNotReadyToNavStartupTarget()");
        EventGeneric eventGeneric = ServiceManager.mGenericEventFactory.newEvent(1330096, 1330014, 3499015);
        ASLNavigationEventFactory.sendEventToService(eventGeneric);
    }

    public void sendEvMapInstanceMainReady() {
        this.getLOGGER().trace("sendEvMapInstanceMainReady()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499014);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapInstanceMainReadyToNavStartupTarget() {
        this.getLOGGER().trace("sendEvMapInstanceMainReadyToNavStartupTarget()");
        EventGeneric eventGeneric = ServiceManager.mGenericEventFactory.newEvent(1330096, 1330014, 3499014);
        ASLNavigationEventFactory.sendEventToService(eventGeneric);
    }

    public void sendEvMapInstanceMapInMapNotReady() {
        this.getLOGGER().trace("sendEvMapInstanceMapInMapNotReady()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499017);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapInstanceMapInMapNotReadyToNavStartupTarget() {
        this.getLOGGER().trace("sendEvMapInstanceMapInMapNotReadyToNavStartupTarget()");
        EventGeneric eventGeneric = ServiceManager.mGenericEventFactory.newEvent(1330096, 1330014, 3499017);
        ASLNavigationEventFactory.sendEventToService(eventGeneric);
    }

    public void sendEvMapInstanceMapInMapReady() {
        this.getLOGGER().trace("sendEvMapInstanceGoogleReady()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499016);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapInstanceMapInMapReadyToNavStartupTarget() {
        this.getLOGGER().trace("sendEvMapInstanceMapInMapReadyToNavStartupTarget()");
        EventGeneric eventGeneric = ServiceManager.mGenericEventFactory.newEvent(1330096, 1330014, 3499016);
        ASLNavigationEventFactory.sendEventToService(eventGeneric);
    }

    public void sendEvMapMainActivateDestinationZoom() {
        this.getLOGGER().trace("sendEventMapMainActivateDestinationZoom()");
        EventGeneric eventGeneric = ServiceManager.mGenericEventFactory.newEvent(3499029);
        ASLNavigationEventFactory.sendEventToService(eventGeneric);
    }

    public void sendEvMapMainActivateFinalDestinationZoom() {
        this.getLOGGER().trace("sendEventMapMainActivateFinalDestinationZoom()");
        EventGeneric eventGeneric = ServiceManager.mGenericEventFactory.newEvent(3499028);
        ASLNavigationEventFactory.sendEventToService(eventGeneric);
    }

    public void sendEvMapMainContentGotoLocation(int n, MapConfiguration mapConfiguration) {
        if (this.getLOGGER().isTraceEnabled()) {
            this.getLOGGER().makeTrace().append("sendEvMapMainContentGotoLocation(type=").append(n).append(", mapConfiguration=").append(mapConfiguration.toString()).append(")").log();
        }
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499004);
        eventGeneric.setInt(0, n);
        eventGeneric.setObject(1, mapConfiguration);
        ASLNavigationEventFactory.sendEventToService(eventGeneric);
    }

    public void sendEvMapMainDrawn() {
        this.getLOGGER().trace("sendEvMapMainDrawn()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499046);
        ASLNavigationEventFactory.sendEventToTarget(1330014, 1330026, eventGeneric);
    }

    public void sendEvMapMainEhSetCategoryVisibility(int[] nArray, boolean[] blArray) {
        this.getLOGGER().trace("sendEvMapMainEhSetCategoryVisibility()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499024);
        eventGeneric.setObject(0, nArray);
        eventGeneric.setObject(1, blArray);
        ASLNavigationEventFactory.sendEventToService(eventGeneric);
    }

    public void sendEvMapMainEhSetCategoryVisibilityResult(int[] nArray) {
        this.getLOGGER().trace("sendEvMapMainEhSetCategoryVisibilityResult()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499026);
        eventGeneric.setObject(0, nArray);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainEhSetCategoryVisibilityToDefault() {
        this.getLOGGER().trace("sendEvMapMainEhSetCategoryVisibilityToDefault()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499025);
        ASLNavigationEventFactory.sendEventToService(eventGeneric);
    }

    public void sendEvMapMainGetInfoForScreenPosition(AbstractTarget abstractTarget, Point point) {
        if (this.getLOGGER().isTraceEnabled()) {
            this.getLOGGER().makeTrace().append("sendEvMapMainGetInfoForScreenPosition(target.id=").append(abstractTarget.getTargetId()).append(", point=").append(point.toString()).log();
        }
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499021);
        eventGeneric.setObject(0, abstractTarget);
        eventGeneric.setObject(1, point);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainGetInfoForScreenPositionResult(AbstractTarget abstractTarget, AbstractTarget abstractTarget2, PosInfo[] posInfoArray) {
        if (this.getLOGGER().isTraceEnabled()) {
            this.getLOGGER().makeTrace().append("sendEvMapMainGetInfoForScreenPositionResult(target.id=").append(abstractTarget2.getTargetId()).append(", posInfos.length=").append(posInfoArray.length).log();
        }
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499022);
        eventGeneric.setObject(0, posInfoArray);
        ASLNavigationEventFactory.sendEventToTarget(abstractTarget.getTargetId(), abstractTarget2.getTargetId(), eventGeneric);
    }

    public void sendEvMapMainGetInfoForScreenPositionResultAsyncException(AbstractTarget abstractTarget, AbstractTarget abstractTarget2, int n, int n2) {
        if (this.getLOGGER().isTraceEnabled()) {
            this.getLOGGER().makeTrace().append("sendEvMapMainGetInfoForScreenPositionResultAsyncException(target.id=").append(abstractTarget2.getTargetId()).append(", requestType=").append(n).append(", errorCode=").append(n2).append(" )").log();
        }
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499054);
        eventGeneric.setInt(0, n);
        eventGeneric.setInt(1, n2);
        ASLNavigationEventFactory.sendEventToTarget(abstractTarget.getTargetId(), abstractTarget2.getTargetId(), eventGeneric);
    }

    public void sendEvMapMainGoogleEarthCheckCrosshairVisibility() {
        if (ASLNavigationMapFactory.getNavigationMapApi().isGoogleEarthActive()) {
            this.getLOGGER().trace("sendEvGooglEarthCheckCrosshairVisibility()");
            EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499043);
            ASLNavigationEventFactory.sendEventToService(eventGeneric);
        }
    }

    public void sendEvMapMainGoogleEarthClearCache() {
        this.getLOGGER().trace("sendEvMapMainGoogleEarthClearCache()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499044);
        ASLNavigationEventFactory.sendEventToService(eventGeneric);
    }

    public void sendEvMapMainGoogleEarthMapPositionChanged() {
        this.getLOGGER().trace("sendEvMapMainGoogleEarthMapPositionChanged()");
        if (ASLNavigationMapFactory.getNavigationMapApi().isGoogleEarthActive()) {
            EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499042);
            ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
        }
    }

    public void sendEvMapMainMapMovedByUser() {
        this.getLOGGER().trace("sendEvMapMainMapMovedByUser()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499040);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainRbSelectAlternativeRoute(int n) {
        this.getLOGGER().trace("sendEvMapMainRbSelectAlternativeRoute()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499027);
        eventGeneric.setInt(0, n);
        ASLNavigationEventFactory.sendEventToService(eventGeneric);
    }

    public void sendEvMapMainRouteVisibility(boolean bl) {
        if (this.getLOGGER().isTraceEnabled()) {
            this.getLOGGER().makeTrace().append("sendEvMapMainRouteVisibility( routeVisible=").append(bl).append(")").log();
        }
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499056);
        eventGeneric.setBoolean(0, bl);
        ASLNavigationEventFactory.sendEventToService(eventGeneric);
    }

    public void sendEvMapMainServiceAvailableChangedGoogleEarth(boolean bl) {
        this.getLOGGER().trace("sendEvServiceAvailableChangeGoogleEarth()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499034);
        eventGeneric.setBoolean(0, bl);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainServiceAvailableChangedGoogleStreetView(boolean bl) {
        this.getLOGGER().trace("sendEvServiceAvailableChangeGoogleStreetView()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499035);
        eventGeneric.setBoolean(0, bl);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainSwitchMapViewerDone() {
        this.getLOGGER().trace("sendEvMapMainSwitchMapViewerDone()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499045);
        ASLNavigationEventFactory.sendEventToService(eventGeneric);
    }

    public void sendEvMapMainTwoFingersZoomDone() {
        this.getLOGGER().trace("sendEvMapMainTwoFingersZoomDone()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499030);
        ASLNavigationEventFactory.sendEventToService(eventGeneric);
    }

    public void sendEvMapMainWaypointModeRecordDestinationFlag(NavLocation navLocation, int n) {
        this.getLOGGER().trace("sendEvMapMainWaypointModeRecordDestinationFlag()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499055);
        eventGeneric.setObject(0, navLocation);
        eventGeneric.setInt(1, n);
        ASLNavigationEventFactory.sendEventToService(eventGeneric);
    }

    public void sendEvMapMainZoomIndexChanged(int n) {
        this.getLOGGER().trace("sendEvMapMainZoomLevelChangedByUser()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499036);
        eventGeneric.setInt(0, n);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainZoomLevelChanged(int n) {
        this.getLOGGER().trace("sendEvMapMainZoomLevelChanged()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499051);
        eventGeneric.setInt(0, n);
        ASLNavigationEventFactory.sendEventToService(eventGeneric);
    }

    public void sendEvMobilityHorizonServiceAvailable() {
        this.getLOGGER().trace("sendEvMobilityHorizonServiceAvailable()");
        ASLNavigationEventFactory.sendEventToAllObservers(ASLNavigationEventFactory.createEvent(3499001));
    }

    public void sendEvMobilityHorizonServiceNotAvailable() {
        this.getLOGGER().trace("sendEvMobilityHorizonServiceAvailable()");
        ASLNavigationEventFactory.sendEventToAllObservers(ASLNavigationEventFactory.createEvent(3499002));
    }

    public void sendEvNaviPostStartup() {
        this.getLOGGER().trace("sendEvNaviPostStartup()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499033);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvShowTMCMessageInMap(TrafficMessageDetails trafficMessageDetails) {
        this.getLOGGER().trace("sendEvShowTMCMessageInMap()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499007);
        eventGeneric.setObject(0, trafficMessageDetails);
        ASLNavigationEventFactory.sendEventToService(eventGeneric);
    }

    private IExtLogger getLOGGER() {
        if (this.LOGGER == null) {
            this.LOGGER = ASLNavigationUtilFactory.getNavigationUtilApi().getExtLogger(16384, "[ASLNavigationInternalAPIImpl]");
        }
        return this.LOGGER;
    }

    public void sendEvMapInMapPerspectiveChanged() {
        this.getLOGGER().trace("sendEvMapInMapPerspectiveChanged()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499059);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapInMapZoomLevelChanged() {
        this.getLOGGER().trace("sendEvMapInMapZoomLevelChanged()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499060);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainGoogleStreetViewAvailable(boolean bl, int n, int n2) {
        this.getLOGGER().trace("sendEvMapMainGoogleStreetViewAvailable()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499062);
        eventGeneric.setBoolean(0, bl);
        eventGeneric.setInt(1, n);
        eventGeneric.setInt(2, n2);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainSpeechRecognizerActive() {
        this.getLOGGER().trace("sendEvMapMainSpeechRecognizerActive()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499063);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainSpeechRecognizerInactive() {
        this.getLOGGER().trace("sendEvMapMainSpeechRecognizerInactive()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499064);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public boolean isMainMapReady() {
        return ASLNavigationServiceMainMapDatapool.getInstance().isMapReady();
    }

    public void sendEvKombiMapDisplayableMapHidden() {
        this.getLOGGER().trace("sendEvKombiMapDisplayableMapHidden()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499065);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvKombiMapDisplayableMapShown() {
        this.getLOGGER().trace("sendEvKombiMapDisplayableMapShown()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499066);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapViewSwitchToABT() {
        this.getLOGGER().trace("sendEvMapViewSwitchToABT()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499067);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapViewSwitchToKombi() {
        this.getLOGGER().trace("sendEvMapViewSwitchToKombi()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499068);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainGuidanceStateChanged(int n) {
        this.getLOGGER().trace("sendEvMapMainGuidanceStateChanged()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499070);
        eventGeneric.setInt(0, n);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapForwardTrafficVisibilityToKombi(boolean bl, boolean bl2) {
        this.getLOGGER().trace("sendEvMapFowardTrafficVisibilityToKombi()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499071);
        eventGeneric.setBoolean(0, bl);
        eventGeneric.setBoolean(1, bl2);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapForwardTrafficIncidentVisibilityToKombi(boolean bl) {
        this.getLOGGER().trace("sendEvMapForwardTrafficIncidentVisibilityToKombi()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(1073744781);
        eventGeneric.setBoolean(0, bl);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendMapViewMapSwitchFinished() {
        this.getLOGGER().trace("sendMapViewMapSwitchFinished()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499072);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendMapMainSetStreetViewPosition(NavLocationWgs84 navLocationWgs84) {
        this.getLOGGER().trace("sendMapMainSetStreetViewPosition()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499073);
        eventGeneric.setObject(0, navLocationWgs84);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendMapViewMapTriggerSwitch() {
        this.getLOGGER().trace("sendMapViewMapTriggerSwitch()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499074);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainHeadingValueChanged(int n) {
        this.getLOGGER().trace("sendEvMapMainHeadingValueChanged()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499075);
        eventGeneric.setInt(0, n);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainZoomValueChanged(int n) {
        this.getLOGGER().trace("sendEvMapMainZoomValueChanged()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499076);
        eventGeneric.setInt(0, n);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainAltitudeValueChanged(int n) {
        this.getLOGGER().trace("sendEvMapMainAltitudeValueChanged()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499077);
        eventGeneric.setInt(0, n);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainAutozoomStatusChanged(boolean bl) {
        this.getLOGGER().trace("sendEvMapMainAutozoomStatusChanged()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499078);
        eventGeneric.setBoolean(0, bl);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapVisibleInAnotherContext(boolean bl) {
        this.getLOGGER().trace("sendEvMapVisibleInAnotherContext()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499079);
        eventGeneric.setBoolean(0, bl);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainOrientationChanged(int n) {
        this.getLOGGER().trace("sendEvMapMainOrientationChanged()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499080);
        eventGeneric.setInt(0, n);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainViewTypeChanged(int n) {
        this.getLOGGER().trace("sendEvMapMainViewTypeChanged()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499081);
        eventGeneric.setInt(0, n);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainMapPerspectiveStateChanged(int n) {
        this.getLOGGER().trace("sendEvMapMainMapPerspectiveStateChanged()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499085);
        eventGeneric.setInt(0, n);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainMapModeChanged(int n) {
        this.getLOGGER().trace("sendEvMapMainMapModeChanged()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499082);
        eventGeneric.setInt(0, n);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainActivateOverviewZoom() {
        this.getLOGGER().trace("sendEvMapMainActivateOverviewZoom()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(1073742416);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainHotPointChanged(int n, int n2) {
        this.getLOGGER().trace("sendEvMapMainHotPointChanged()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(1073744665);
        eventGeneric.setInt(0, n);
        eventGeneric.setInt(1, n2);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainCarsorPositionChanged(int n, int n2) {
        this.getLOGGER().trace("sendEvMapMainCarsorPositionChanged()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(1073742415);
        eventGeneric.setInt(0, n);
        eventGeneric.setInt(1, n2);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainMapTypeChanged(int n) {
        this.getLOGGER().makeTrace().append("sendEvMapMainMapTypeChanged(").append(n).append(" )").log();
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499083);
        eventGeneric.setInt(0, n);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapICMapServiceStateChanged(int n) {
        this.getLOGGER().trace("sendEvMapICMapServiceStateChanged()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499084);
        eventGeneric.setInt(0, n);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public boolean isAutozoomActivated() {
        return PersistedMapSetup.getInstance().isAutoZoomMainMap();
    }

    public boolean isAutozoomDeactivatedWhileDrag() {
        return MapViewerDatapoolShared.getInstance().isAutozoomDeactivatedWhileDrag();
    }

    public void sendEvAutozoomForcedByOtherContext(boolean bl) {
        this.getLOGGER().trace("sendEvAutozoomForcedByOtherContext()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499087);
        eventGeneric.setBoolean(0, bl);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainSetZoomArea(int n, int n2, int n3, int n4) {
        this.getLOGGER().trace("sendEvMapMainSetZoomArea()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499091);
        eventGeneric.setInt(0, n);
        eventGeneric.setInt(1, n2);
        eventGeneric.setInt(2, n3);
        eventGeneric.setInt(3, n4);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainMapLastTypeChanged(int n) {
        this.getLOGGER().makeTrace().append("sendEvMapMainMapLastTypeChanged(").append(n).append(" )").log();
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499092);
        eventGeneric.setInt(0, n);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvGoogleEarthDataStatusChanged(int n) {
        this.getLOGGER().trace("sendEvGoogleEarthDataStatusChanged()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499093);
        eventGeneric.setInt(0, n);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapMainSwitchMapViewerRunning() {
        this.getLOGGER().trace("sendEvMapMainSwitchMapViewerRunning()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499094);
        ASLNavigationEventFactory.sendEventToAllObservers(eventGeneric);
    }

    public void sendEvMapSwitcherReady() {
        this.getLOGGER().trace("sendEvMapSwitcherReady()");
        EventGeneric eventGeneric = ASLNavigationEventFactory.createEvent(3499095);
        ASLNavigationEventFactory.sendEventToService(eventGeneric);
    }
}

