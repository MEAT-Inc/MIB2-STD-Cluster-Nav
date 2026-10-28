/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.asl.service;

import de.vw.mib.asl.api.navigation.util.ASLNavigationUtilFactory;
import de.vw.mib.asl.api.navigation.util.IExtLogger;
import de.vw.mib.asl.framework.internal.framework.ServiceManager;
import de.vw.mib.asl.framework.internal.framework.id.PreRegisteredIds;
import de.vw.mib.genericevents.AbstractTarget;
import de.vw.mib.genericevents.EventGeneric;
import de.vw.mib.genericevents.GenericEventException;
import de.vw.mib.genericevents.ServiceRegister;
import org.dsi.ifc.global.NavLocationWgs84;
import org.dsi.ifc.map.PosInfo;

public class ASLNavigationServiceMainMapEvents {
    private static IExtLogger LOGGER = null;
    private static final int[] MAINMAP_SERVICES = new int[]{3400026, 3400022, 3400024, 3400025, 3400011, 3400016, 3400017, 3400020, 3400019, 3400015, 3400014, 3400013, 3400029, 3499028, 3499029, 3499030, 3499063, 3499064, 3499065, 3499066, 3499067, 3499068};
    static final int[] ASL_OBSERVERS = new int[]{3499030};
    static final int[] ATTRIBUTES_MAPVIEWERCONTROL = new int[]{10, 9, 47, 46, 13, 1, 8};
    static final int[] ATTRITBUTES_NAVIGATION = new int[]{52};

    private static IExtLogger getLogger() {
        if (LOGGER == null) {
            LOGGER = ASLNavigationUtilFactory.getNavigationUtilApi().getExtLogger(65536, "[ASLNavigationServiceMainMapEvents]");
        }
        return LOGGER;
    }

    private static EventGeneric createEvent(int n) {
        return ServiceManager.mGenericEventFactory.newEvent(n);
    }

    static void sendEventToTarget(AbstractTarget abstractTarget, EventGeneric eventGeneric) {
        try {
            eventGeneric.setReceiverTargetId(abstractTarget.getTargetId());
            if (ASLNavigationServiceMainMapEvents.getLogger().isTraceEnabled()) {
                ASLNavigationServiceMainMapEvents.getLogger().makeTrace().append("sendEventToTarget(evId=").append(eventGeneric.getServiceId()).append(", targetId=").append(eventGeneric.getReceiverTargetId()).append(")").log();
            }
            ServiceManager.eventMain.getEventDispatcher().send(eventGeneric);
        }
        catch (GenericEventException genericEventException) {
            ASLNavigationServiceMainMapEvents.getLogger().error(genericEventException.toString());
        }
    }

    private static void sendEventToService(EventGeneric eventGeneric) {
        try {
            if (ASLNavigationServiceMainMapEvents.getLogger().isTraceEnabled()) {
                ASLNavigationServiceMainMapEvents.getLogger().makeTrace().append("sendEventToService(serviceId=").append(eventGeneric.getServiceId()).append(")").log();
            }
            ServiceManager.eventMain.getEventDispatcher().send(eventGeneric);
        }
        catch (GenericEventException genericEventException) {
            ASLNavigationServiceMainMapEvents.getLogger().error(genericEventException.toString());
        }
    }

    static void registerServices() {
        ServiceRegister serviceRegister = ServiceManager.eventMain.getServiceRegister();
        for (int i = 0; i < MAINMAP_SERVICES.length; ++i) {
            serviceRegister.registerService(MAINMAP_SERVICES[i], 0x144BBB, MAINMAP_SERVICES[i], true);
        }
    }

    public static void preRegisterServices() {
        for (int i = 0; i < MAINMAP_SERVICES.length; ++i) {
            PreRegisteredIds.addServiceOrObserverToArray(0, 0x144BBB, MAINMAP_SERVICES[i], true);
        }
    }

    static void sendEventServiceError(AbstractTarget abstractTarget, int n) {
        ASLNavigationServiceMainMapEvents.getLogger().makeError().append("sendEventServiceError( targetId=").append(abstractTarget.getTargetId()).append(", errorCode=").append(n).append(" )").log();
        EventGeneric eventGeneric = ASLNavigationServiceMainMapEvents.createEvent(3400022);
        eventGeneric.setInt(0, n);
        ASLNavigationServiceMainMapEvents.sendEventToTarget(abstractTarget, eventGeneric);
    }

    static void sendEventServiceStatusChange(boolean bl) {
        EventGeneric eventGeneric = bl ? ServiceManager.mGenericEventFactory.newEvent(3400024) : ServiceManager.mGenericEventFactory.newEvent(3400025);
        ASLNavigationServiceMainMapEvents.sendEventToService(eventGeneric);
    }

    static void sendEventMapLocked(AbstractTarget abstractTarget) {
        EventGeneric eventGeneric = ASLNavigationServiceMainMapEvents.createEvent(3400017);
        ASLNavigationServiceMainMapEvents.sendEventToTarget(abstractTarget, eventGeneric);
    }

    static void sendEventMapClickInMapResult(AbstractTarget abstractTarget, PosInfo[] posInfoArray) {
        EventGeneric eventGeneric = ASLNavigationServiceMainMapEvents.createEvent(3400011);
        eventGeneric.setObject(0, posInfoArray);
        ASLNavigationServiceMainMapEvents.sendEventToTarget(abstractTarget, eventGeneric);
    }

    static void sendEventMapZoomListUpdate(AbstractTarget abstractTarget, int[] nArray) {
        EventGeneric eventGeneric = ASLNavigationServiceMainMapEvents.createEvent(3400020);
        eventGeneric.setObject(0, nArray);
        ASLNavigationServiceMainMapEvents.sendEventToTarget(abstractTarget, eventGeneric);
    }

    static void sendEventMapPositionUpdate(AbstractTarget abstractTarget, NavLocationWgs84 navLocationWgs84) {
        EventGeneric eventGeneric = ASLNavigationServiceMainMapEvents.createEvent(3400016);
        eventGeneric.setObject(0, navLocationWgs84);
        ASLNavigationServiceMainMapEvents.sendEventToTarget(abstractTarget, eventGeneric);
    }

    static void sendEventMapZoomLevelUpdate(AbstractTarget abstractTarget, int n, int n2) {
        EventGeneric eventGeneric = ASLNavigationServiceMainMapEvents.createEvent(3400019);
        eventGeneric.setInt(0, n);
        eventGeneric.setInt(1, n2);
        ASLNavigationServiceMainMapEvents.sendEventToTarget(abstractTarget, eventGeneric);
    }

    static void sendEventMapGoToLocationMapReady(AbstractTarget abstractTarget) {
        EventGeneric eventGeneric = ASLNavigationServiceMainMapEvents.createEvent(3400013);
        ASLNavigationServiceMainMapEvents.sendEventToTarget(abstractTarget, eventGeneric);
    }

    static void sendEventMapLayersAvailable(AbstractTarget abstractTarget, int[] nArray) {
        EventGeneric eventGeneric = ASLNavigationServiceMainMapEvents.createEvent(3400014);
        eventGeneric.setObject(0, nArray);
        ASLNavigationServiceMainMapEvents.sendEventToTarget(abstractTarget, eventGeneric);
    }

    static void sendEventMapLayersVisibleUpdate(AbstractTarget abstractTarget, int[] nArray) {
        EventGeneric eventGeneric = ASLNavigationServiceMainMapEvents.createEvent(3400015);
        eventGeneric.setObject(0, nArray);
        ASLNavigationServiceMainMapEvents.sendEventToTarget(abstractTarget, eventGeneric);
    }

    static void sendEventZoomIn() {
        EventGeneric eventGeneric = ServiceManager.mGenericEventFactory.newEvent(1073742420);
        ASLNavigationServiceMainMapEvents.sendEventToService(eventGeneric);
    }

    static void sendEventZoomOut() {
        EventGeneric eventGeneric = ServiceManager.mGenericEventFactory.newEvent(1073742422);
        ASLNavigationServiceMainMapEvents.sendEventToService(eventGeneric);
    }

    static void sendEventTwoFingerZoomed(int n, int n2, int n3, int n4) {
        EventGeneric eventGeneric = ServiceManager.mGenericEventFactory.newEvent(1074841824);
        eventGeneric.setInt(0, n);
        eventGeneric.setInt(1, n2);
        eventGeneric.setInt(2, n3);
        eventGeneric.setInt(3, n4);
        ASLNavigationServiceMainMapEvents.sendEventToService(eventGeneric);
    }

    static void sendEventToggleOverviewZoom() {
        EventGeneric eventGeneric = ServiceManager.mGenericEventFactory.newEvent(1073742416);
        ASLNavigationServiceMainMapEvents.sendEventToService(eventGeneric);
    }

    static void sendEventCenterMapToCCP() {
        EventGeneric eventGeneric = ServiceManager.mGenericEventFactory.newEvent(1073742409);
        ASLNavigationServiceMainMapEvents.sendEventToService(eventGeneric);
    }

    static void sendEventToggleAutozoom() {
        EventGeneric eventGeneric = ServiceManager.mGenericEventFactory.newEvent(1073742389);
        ASLNavigationServiceMainMapEvents.sendEventToService(eventGeneric);
    }

    static void sendEventServiceInit() {
        EventGeneric eventGeneric = ServiceManager.mGenericEventFactory.newEvent(3400026);
        ASLNavigationServiceMainMapEvents.sendEventToService(eventGeneric);
    }

    static void sendEventClickInMap(int n, int n2, int n3) {
        EventGeneric eventGeneric = ServiceManager.mGenericEventFactory.newEvent(1073742411);
        eventGeneric.setInt(0, n3);
        eventGeneric.setInt(1, n);
        eventGeneric.setInt(2, n2);
        ASLNavigationServiceMainMapEvents.sendEventToService(eventGeneric);
    }

    static void sendEventServiceErrorAPICall(AbstractTarget abstractTarget, int n, int n2) {
        ASLNavigationServiceMainMapEvents.getLogger().makeError().append("sendEventServiceErrorAPICall( targetId=").append(abstractTarget).append(", requestType=").append(n).append(", errorCode=").append(n2).append(" )").log();
        EventGeneric eventGeneric = ASLNavigationServiceMainMapEvents.createEvent(3400022);
        eventGeneric.setInt(0, 6);
        eventGeneric.setInt(1, n);
        eventGeneric.setInt(2, n2);
        ASLNavigationServiceMainMapEvents.sendEventToTarget(abstractTarget, eventGeneric);
    }

    public static void sendEventKombiMapSwitchState(int n) {
        EventGeneric eventGeneric = ServiceManager.mGenericEventFactory.newEvent(3400029);
        eventGeneric.setInt(0, n);
        ASLNavigationServiceMainMapEvents.sendEventToService(eventGeneric);
    }
}

