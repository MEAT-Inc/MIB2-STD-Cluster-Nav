/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.google.streetview;

import de.vw.mib.asl.api.navigation.map.ASLNavigationMapFactory;
import de.vw.mib.asl.api.navigation.util.ASLNavigationUtilFactory;
import de.vw.mib.asl.api.navigation.util.IExtLogger;
import de.vw.mib.asl.api.online.ASLOnlineCoreServices;
import de.vw.mib.asl.api.online.ASLOnlineFactory;
import de.vw.mib.asl.framework.api.dsiproxy.DSIProxy;
import de.vw.mib.asl.framework.api.dsiproxy.DSIProxyFactory;
import de.vw.mib.asl.framework.api.dsiproxy.DSIServiceStateListener;
import de.vw.mib.asl.framework.internal.framework.AbstractASLHsmTarget;
import de.vw.mib.asl.internal.navigation.AbstractResettableTarget;
import de.vw.mib.asl.internal.navigation.map.dsi.DSIMapViewerStreetViewCtrlVW;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.google.streetview.DSIMapViewerStreetViewCtrlTargetData;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.google.streetview.DSIMapViewerStreetViewCtrlTargetDatapool;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.google.streetview.DSIMapViewerStreetViewCtrlVWImpl;
import de.vw.mib.genericevents.AbstractTarget;
import de.vw.mib.genericevents.EventGeneric;
import de.vw.mib.genericevents.GenericEvents;
import java.util.HashMap;
import org.dsi.ifc.base.DSIListener;
import org.dsi.ifc.map.DSIMapViewerStreetViewCtrl;
import org.dsi.ifc.map.DSIMapViewerStreetViewCtrlListener;

public class DSIMapViewerStreetViewCtrlTarget
extends AbstractResettableTarget {
    protected final IExtLogger LOGGER = ASLNavigationUtilFactory.getNavigationUtilApi().getExtLogger(65536, "[DSIMapViewerStreetViewCtrlTarget]");
    protected final DSIMapViewerStreetViewCtrlTargetDatapool datapool;
    private final ASLOnlineCoreServices onlineCoreServices;
    private int[] ASL_SERVICES = new int[]{3499035};
    private final DSIProxy proxy = DSIProxyFactory.getDSIProxyAPI().getDSIProxy();
    static /* synthetic */ Class class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrl;
    static /* synthetic */ Class class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrlListener;
    static /* synthetic */ Class class$org$dsi$ifc$map$DSIMapViewerGoogleCtrlListener;

    public DSIMapViewerStreetViewCtrlTarget(GenericEvents genericEvents, int n, String string) throws Exception {
        super(genericEvents, n, string);
        this.datapool = new DSIMapViewerStreetViewCtrlTargetDatapool();
        this.onlineCoreServices = ASLOnlineFactory.getOnlineCoreServices();
    }

    public DSIMapViewerStreetViewCtrlVW createStreetViewCtrl(AbstractTarget abstractTarget, int[] nArray) {
        DSIMapViewerStreetViewCtrlTargetData dSIMapViewerStreetViewCtrlTargetData;
        this.LOGGER.trace("createStreetViewCtrl()");
        Integer n = new Integer(abstractTarget.getTargetId());
        if (this.datapool.getServiceInstances().containsKey(n)) {
            this.LOGGER.makeWarn().append("the target '").append(n).append("' is already registred").log();
            dSIMapViewerStreetViewCtrlTargetData = (DSIMapViewerStreetViewCtrlTargetData)this.datapool.getServiceInstances().get(n);
        } else {
            dSIMapViewerStreetViewCtrlTargetData = this.createTargetData(abstractTarget, nArray);
            this.datapool.getServiceInstances().put(n, dSIMapViewerStreetViewCtrlTargetData);
            if (this.datapool.isServiceAvailable()) {
                this.initMapViewerStreetViewCtrl(dSIMapViewerStreetViewCtrlTargetData);
            }
        }
        return dSIMapViewerStreetViewCtrlTargetData.getDsiMapViewerStreetViewCtrlVW();
    }

    private DSIMapViewerStreetViewCtrlTargetData createTargetData(AbstractTarget abstractTarget, int[] nArray) {
        this.LOGGER.trace("initMapViewerStreetViewCtrl()");
        DSIMapViewerStreetViewCtrlTargetData dSIMapViewerStreetViewCtrlTargetData = new DSIMapViewerStreetViewCtrlTargetData();
        dSIMapViewerStreetViewCtrlTargetData.setDsiMapViewerStreetViewCtrlVW(new DSIMapViewerStreetViewCtrlVWImpl());
        dSIMapViewerStreetViewCtrlTargetData.setAttributes(nArray);
        dSIMapViewerStreetViewCtrlTargetData.setTarget(abstractTarget);
        return dSIMapViewerStreetViewCtrlTargetData;
    }

    public DSIMapViewerStreetViewCtrlTargetDatapool getDatapool() {
        return this.datapool;
    }

    public void gotEvent(EventGeneric eventGeneric) throws Exception {
        switch (eventGeneric.getReceiverEventId()) {
            case 106: {
                this.gotEventPowerOn();
                break;
            }
            case 101001: {
                this.gotEventnaviTargetGoOn();
                break;
            }
            default: {
                return;
            }
        }
    }

    private void gotEventnaviTargetGoOn() {
        this.initServiceStateListener();
    }

    private void gotEventPowerOn() {
        this.LOGGER.trace("gotEventPowerOn()");
        this.init();
    }

    private void init() {
        this.LOGGER.trace("init()");
        this.initASL();
    }

    private void initASL() {
        this.LOGGER.trace("initASL()");
        this.registerServices(this.ASL_SERVICES, true);
    }

    private void initMapViewerStreetViewCtrl(DSIMapViewerStreetViewCtrlTargetData dSIMapViewerStreetViewCtrlTargetData) {
        this.LOGGER.trace("initMapViewerStreetViewCtrl()");
        this.initMapViewerStreetViewCtrlDSI(dSIMapViewerStreetViewCtrlTargetData);
        this.initMapViewerStreetViewCtrlDSIListener(dSIMapViewerStreetViewCtrlTargetData);
        this.initMapViewerStreetViewCtrlResponseListener(dSIMapViewerStreetViewCtrlTargetData);
        this.initMapViewerStreetViewCtrlAttributes(dSIMapViewerStreetViewCtrlTargetData);
        dSIMapViewerStreetViewCtrlTargetData.getDsiMapViewerStreetViewCtrlVW().setFacadeEnabled(true);
    }

    private void initMapViewerStreetViewCtrlAttributes(DSIMapViewerStreetViewCtrlTargetData dSIMapViewerStreetViewCtrlTargetData) {
        int[] nArray = dSIMapViewerStreetViewCtrlTargetData.getAttributes();
        if (nArray != null && nArray.length > 0) {
            dSIMapViewerStreetViewCtrlTargetData.getDsiMapViewerStreetViewCtrl().setNotification(nArray, (DSIListener)dSIMapViewerStreetViewCtrlTargetData.getDsiMapViewerStreetViewCtrlListener());
        }
    }

    private void initMapViewerStreetViewCtrlDSI(DSIMapViewerStreetViewCtrlTargetData dSIMapViewerStreetViewCtrlTargetData) {
        if (dSIMapViewerStreetViewCtrlTargetData.getDsiMapViewerStreetViewCtrl() == null) {
            DSIMapViewerStreetViewCtrl dSIMapViewerStreetViewCtrl = (DSIMapViewerStreetViewCtrl)this.proxy.getService(dSIMapViewerStreetViewCtrlTargetData.getTarget(), class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrl == null ? (class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrl = DSIMapViewerStreetViewCtrlTarget.class$("org.dsi.ifc.map.DSIMapViewerStreetViewCtrl")) : class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrl);
            dSIMapViewerStreetViewCtrlTargetData.setDsiMapViewerStreetViewCtrl(dSIMapViewerStreetViewCtrl);
            dSIMapViewerStreetViewCtrlTargetData.getDsiMapViewerStreetViewCtrlVW().setMapViewerStreetViewCtrl(dSIMapViewerStreetViewCtrl);
        }
    }

    private void initMapViewerStreetViewCtrlDSIListener(DSIMapViewerStreetViewCtrlTargetData dSIMapViewerStreetViewCtrlTargetData) {
        if (dSIMapViewerStreetViewCtrlTargetData.getDsiMapViewerStreetViewCtrlListener() == null) {
            DSIMapViewerStreetViewCtrlListener dSIMapViewerStreetViewCtrlListener;
            AbstractTarget abstractTarget = dSIMapViewerStreetViewCtrlTargetData.getTarget();
            if (abstractTarget instanceof AbstractASLHsmTarget) {
                AbstractASLHsmTarget abstractASLHsmTarget = (AbstractASLHsmTarget)abstractTarget;
                dSIMapViewerStreetViewCtrlListener = (DSIMapViewerStreetViewCtrlListener)this.proxy.getAdapterFactory().createDSIListenerMethodAdapter(abstractASLHsmTarget.getHsm(), class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrlListener == null ? (class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrlListener = DSIMapViewerStreetViewCtrlTarget.class$("org.dsi.ifc.map.DSIMapViewerStreetViewCtrlListener")) : class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrlListener);
            } else {
                dSIMapViewerStreetViewCtrlListener = (DSIMapViewerStreetViewCtrlListener)this.proxy.getAdapterFactory().createDSIListenerMethodAdapter(abstractTarget, class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrlListener == null ? (class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrlListener = DSIMapViewerStreetViewCtrlTarget.class$("org.dsi.ifc.map.DSIMapViewerStreetViewCtrlListener")) : class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrlListener);
            }
            dSIMapViewerStreetViewCtrlTargetData.setDsiMapViewerStreetViewCtrlListener(dSIMapViewerStreetViewCtrlListener);
        }
    }

    private void initMapViewerStreetViewCtrlResponseListener(DSIMapViewerStreetViewCtrlTargetData dSIMapViewerStreetViewCtrlTargetData) {
        this.proxy.addResponseListener(dSIMapViewerStreetViewCtrlTargetData.getTarget(), class$org$dsi$ifc$map$DSIMapViewerGoogleCtrlListener == null ? (class$org$dsi$ifc$map$DSIMapViewerGoogleCtrlListener = DSIMapViewerStreetViewCtrlTarget.class$("org.dsi.ifc.map.DSIMapViewerGoogleCtrlListener")) : class$org$dsi$ifc$map$DSIMapViewerGoogleCtrlListener, dSIMapViewerStreetViewCtrlTargetData.getDsiMapViewerStreetViewCtrlListener());
    }

    private void initServiceStateListener() {
        this.LOGGER.trace("initServiceStateListener()");
        DSIServiceStateListener dSIServiceStateListener = new DSIServiceStateListener(){

            public void registered(String string, int n) {
                if (string.equals((class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrl == null ? (class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrl = DSIMapViewerStreetViewCtrlTarget.class$("org.dsi.ifc.map.DSIMapViewerStreetViewCtrl")) : class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrl).getName()) && !DSIMapViewerStreetViewCtrlTarget.this.isFirstStartupDone) {
                    DSIMapViewerStreetViewCtrlTarget.this.isFirstStartupDone = true;
                    if (DSIMapViewerStreetViewCtrlTarget.this.datapool.isServiceAvailable()) {
                        DSIMapViewerStreetViewCtrlTarget.this.LOGGER.error("the service 'DSIMapViewerStreetViewCtrl' is already registered, DSIServiceStateListener().registered(String, int) will be ignored.");
                        return;
                    }
                    DSIMapViewerStreetViewCtrlTarget.this.serviceInstancesInit();
                }
            }

            public void unregistered(String string, int n) {
                if (string.equals((class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrl == null ? (class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrl = DSIMapViewerStreetViewCtrlTarget.class$("org.dsi.ifc.map.DSIMapViewerStreetViewCtrl")) : class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrl).getName())) {
                    if (!DSIMapViewerStreetViewCtrlTarget.this.datapool.isServiceAvailable()) {
                        DSIMapViewerStreetViewCtrlTarget.this.LOGGER.error("the service 'DSIMapViewerStreetViewCtrl' is not yet registered, DSIServiceStateListener().unregistered(String, int) will be ignored.");
                        return;
                    }
                    DSIMapViewerStreetViewCtrlTarget.this.serviceInstancesDisable();
                }
            }
        };
        this.proxy.addServiceStateListener(class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrl == null ? (class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrl = DSIMapViewerStreetViewCtrlTarget.class$("org.dsi.ifc.map.DSIMapViewerStreetViewCtrl")) : class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrl, dSIServiceStateListener);
    }

    protected void serviceInstancesInit() {
        this.LOGGER.trace("serviceInstanceInit()");
        this.datapool.setServiceAvailable(true);
        for (DSIMapViewerStreetViewCtrlTargetData dSIMapViewerStreetViewCtrlTargetData : this.datapool.getServiceInstances().values()) {
            this.initMapViewerStreetViewCtrl(dSIMapViewerStreetViewCtrlTargetData);
        }
        ASLNavigationMapFactory.getNavigationMapApi().sendEvMapMainServiceAvailableChangedGoogleStreetView(true);
    }

    protected void serviceInstancesDisable() {
        this.LOGGER.trace("streetViewDisable()");
        this.datapool.setServiceAvailable(false);
        ASLNavigationMapFactory.getNavigationMapApi().sendEvMapMainServiceAvailableChangedGoogleStreetView(false);
        for (DSIMapViewerStreetViewCtrlTargetData dSIMapViewerStreetViewCtrlTargetData : this.datapool.getServiceInstances().values()) {
            dSIMapViewerStreetViewCtrlTargetData.getDsiMapViewerStreetViewCtrlVW().setFacadeEnabled(false);
        }
    }

    public void reset(HashMap hashMap) {
        if (this.isDsiInHashMap(hashMap, (class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrl == null ? (class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrl = DSIMapViewerStreetViewCtrlTarget.class$("org.dsi.ifc.map.DSIMapViewerStreetViewCtrl")) : class$org$dsi$ifc$map$DSIMapViewerStreetViewCtrl).getName(), 0)) {
            if (this.LOGGER.isTraceEnabled()) {
                this.LOGGER.trace("resetting values after DSI restart");
            }
            this.serviceInstancesInit();
        } else if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.trace("no reset necessary because restarted DSI(s) is/are not used in target");
        }
    }

    static /* synthetic */ Class class$(String string) {
        try {
            return Class.forName(string);
        }
        catch (ClassNotFoundException classNotFoundException) {
            throw new NoClassDefFoundError().initCause(classNotFoundException);
        }
    }
}

