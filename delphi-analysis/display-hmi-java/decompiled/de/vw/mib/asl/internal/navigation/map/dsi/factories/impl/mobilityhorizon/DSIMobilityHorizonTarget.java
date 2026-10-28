/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.mobilityhorizon;

import de.vw.mib.asl.api.navigation.map.ASLNavigationMapFactory;
import de.vw.mib.asl.api.navigation.util.ASLNavigationUtilFactory;
import de.vw.mib.asl.api.navigation.util.IExtLogger;
import de.vw.mib.asl.framework.api.dsiproxy.DSIProxy;
import de.vw.mib.asl.framework.api.dsiproxy.DSIProxyFactory;
import de.vw.mib.asl.framework.api.dsiproxy.DSIServiceStateListener;
import de.vw.mib.asl.framework.internal.framework.AbstractASLHsmTarget;
import de.vw.mib.asl.internal.navigation.map.dsi.DSIMobilityHorizonVW;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.mobilityhorizon.DSIMobilityHorizonDatapool;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.mobilityhorizon.DSIMobilityHorizonTargetData;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.mobilityhorizon.DSIMobilityHorizonTargetDatapool;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.mobilityhorizon.DSIMobilityHorizonVWImpl;
import de.vw.mib.genericevents.AbstractTarget;
import de.vw.mib.genericevents.EventGeneric;
import de.vw.mib.genericevents.GenericEvents;
import org.dsi.ifc.base.DSIListener;
import org.dsi.ifc.mobilityhorizon.DSIMobilityHorizon;
import org.dsi.ifc.mobilityhorizon.DSIMobilityHorizonListener;

public class DSIMobilityHorizonTarget
extends AbstractTarget {
    protected final IExtLogger logger;
    protected final DSIMobilityHorizonTargetDatapool datapool;
    private final DSIProxy proxy = DSIProxyFactory.getDSIProxyAPI().getDSIProxy();
    private static final int[] ASL_SERVICES = new int[]{3499001, 3499002};
    private static boolean aslServiceAlreadyRegistered = false;
    static /* synthetic */ Class class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizon;
    static /* synthetic */ Class class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizonListener;

    public DSIMobilityHorizonTarget(DSIMobilityHorizonDatapool dSIMobilityHorizonDatapool, GenericEvents genericEvents, int n, String string) throws Exception {
        super(genericEvents, n, string);
        this.logger = ASLNavigationUtilFactory.getNavigationUtilApi().getExtLogger(65536, "[DSIMobilityHorizonTarget]");
        this.datapool = new DSIMobilityHorizonTargetDatapool(dSIMobilityHorizonDatapool);
        if (!aslServiceAlreadyRegistered) {
            aslServiceAlreadyRegistered = true;
            this.registerServices(ASL_SERVICES, false);
        }
    }

    public DSIMobilityHorizonVW createMobilityHorizon(AbstractTarget abstractTarget, int[] nArray) {
        DSIMobilityHorizonTargetData dSIMobilityHorizonTargetData;
        if (abstractTarget == null) {
            this.logger.error("createMobilityHorizon( AbstractTarget target, int[] attributes ) - the target can't be null, execution stopped");
            return null;
        }
        Integer n = new Integer(abstractTarget.getTargetId());
        if (this.datapool.getServiceInstances().containsKey(n)) {
            this.logger.makeWarn().append("the target '").append(n).append("' is already registred").log();
            dSIMobilityHorizonTargetData = (DSIMobilityHorizonTargetData)this.datapool.getServiceInstances().get(n);
        } else {
            dSIMobilityHorizonTargetData = this.createTargetData(abstractTarget, nArray);
            this.datapool.getServiceInstances().put(n, dSIMobilityHorizonTargetData);
            if (this.datapool.isServiceAvailable()) {
                this.initMobilityHorizonTarget(dSIMobilityHorizonTargetData);
            }
        }
        return dSIMobilityHorizonTargetData.getDsiMobilityHorizonVW();
    }

    private DSIMobilityHorizonTargetData createTargetData(AbstractTarget abstractTarget, int[] nArray) {
        DSIMobilityHorizonTargetData dSIMobilityHorizonTargetData = new DSIMobilityHorizonTargetData();
        dSIMobilityHorizonTargetData.setTarget(abstractTarget);
        dSIMobilityHorizonTargetData.setAttributes(nArray);
        dSIMobilityHorizonTargetData.setDsiMobilityHorizonVW(new DSIMobilityHorizonVWImpl(this.datapool.getDsiMobilityHorizonDatapool()));
        return dSIMobilityHorizonTargetData;
    }

    public void gotEvent(EventGeneric eventGeneric) throws Exception {
        switch (eventGeneric.getReceiverEventId()) {
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

    private void initMobilityHorizonTarget(DSIMobilityHorizonTargetData dSIMobilityHorizonTargetData) {
        this.logger.trace("initMobilityHorizonTarget()");
        this.initMobilityHorizonTargetDSI(dSIMobilityHorizonTargetData);
        this.initMobilityHorizonTargetDSIListener(dSIMobilityHorizonTargetData);
        this.initMobilityHorizonTargetResponseListener(dSIMobilityHorizonTargetData);
        this.initMobilityHorizonTargetAttributes(dSIMobilityHorizonTargetData);
        dSIMobilityHorizonTargetData.getDsiMobilityHorizonVW().setFacadeEnabled(true);
    }

    private void initMobilityHorizonTargetAttributes(DSIMobilityHorizonTargetData dSIMobilityHorizonTargetData) {
        int[] nArray = dSIMobilityHorizonTargetData.getAttributes();
        if (nArray != null && nArray.length > 0) {
            dSIMobilityHorizonTargetData.setAttributes(nArray);
            dSIMobilityHorizonTargetData.getDsiMobilityHorizon().setNotification(nArray, (DSIListener)dSIMobilityHorizonTargetData.getDsiMobilityHorizonListener());
        }
    }

    private void initMobilityHorizonTargetDSI(DSIMobilityHorizonTargetData dSIMobilityHorizonTargetData) {
        if (dSIMobilityHorizonTargetData.getDsiMobilityHorizon() == null) {
            AbstractTarget abstractTarget = dSIMobilityHorizonTargetData.getTarget();
            DSIMobilityHorizon dSIMobilityHorizon = (DSIMobilityHorizon)this.proxy.getService(abstractTarget, class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizon == null ? (class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizon = DSIMobilityHorizonTarget.class$("org.dsi.ifc.mobilityhorizon.DSIMobilityHorizon")) : class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizon);
            dSIMobilityHorizonTargetData.getDsiMobilityHorizonVW().setDsiMobilityHorizon(dSIMobilityHorizon);
            dSIMobilityHorizonTargetData.setDsiMobilityHorizon(dSIMobilityHorizon);
        }
    }

    private void initMobilityHorizonTargetDSIListener(DSIMobilityHorizonTargetData dSIMobilityHorizonTargetData) {
        if (dSIMobilityHorizonTargetData.getDsiMobilityHorizonListener() == null) {
            DSIMobilityHorizonListener dSIMobilityHorizonListener;
            AbstractTarget abstractTarget = dSIMobilityHorizonTargetData.getTarget();
            if (abstractTarget instanceof AbstractASLHsmTarget) {
                AbstractASLHsmTarget abstractASLHsmTarget = (AbstractASLHsmTarget)abstractTarget;
                dSIMobilityHorizonListener = (DSIMobilityHorizonListener)this.proxy.getAdapterFactory().createDSIListenerMethodAdapter(abstractASLHsmTarget.getHsm(), class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizonListener == null ? (class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizonListener = DSIMobilityHorizonTarget.class$("org.dsi.ifc.mobilityhorizon.DSIMobilityHorizonListener")) : class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizonListener);
            } else {
                dSIMobilityHorizonListener = (DSIMobilityHorizonListener)this.proxy.getAdapterFactory().createDSIListenerMethodAdapter(abstractTarget, class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizonListener == null ? (class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizonListener = DSIMobilityHorizonTarget.class$("org.dsi.ifc.mobilityhorizon.DSIMobilityHorizonListener")) : class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizonListener);
            }
            dSIMobilityHorizonTargetData.setDsiMobilityHorizonListener(dSIMobilityHorizonListener);
        }
    }

    private void initMobilityHorizonTargetResponseListener(DSIMobilityHorizonTargetData dSIMobilityHorizonTargetData) {
        this.proxy.addResponseListener(dSIMobilityHorizonTargetData.getTarget(), class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizonListener == null ? (class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizonListener = DSIMobilityHorizonTarget.class$("org.dsi.ifc.mobilityhorizon.DSIMobilityHorizonListener")) : class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizonListener, dSIMobilityHorizonTargetData.getDsiMobilityHorizonListener());
    }

    private void initServiceStateListener() {
        DSIServiceStateListener dSIServiceStateListener = new DSIServiceStateListener(){

            public void registered(String string, int n) {
                if (string.equals((class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizon == null ? (class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizon = DSIMobilityHorizonTarget.class$("org.dsi.ifc.mobilityhorizon.DSIMobilityHorizon")) : class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizon).getName())) {
                    if (DSIMobilityHorizonTarget.this.datapool.isServiceAvailable()) {
                        DSIMobilityHorizonTarget.this.logger.error("the service 'DSIMobilityHorizon' is already registered, DSIServiceStateListener().registered(String, int) will be ignored.");
                        return;
                    }
                    DSIMobilityHorizonTarget.this.serviceInstancesInit();
                }
            }

            public void unregistered(String string, int n) {
                if (string.equals((class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizon == null ? (class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizon = DSIMobilityHorizonTarget.class$("org.dsi.ifc.mobilityhorizon.DSIMobilityHorizon")) : class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizon).getName())) {
                    if (!DSIMobilityHorizonTarget.this.datapool.isServiceAvailable()) {
                        DSIMobilityHorizonTarget.this.logger.error("the service 'DSIMobilityHorizon' is not yet registered, DSIServiceStateListener().unregistered(String, int) will be ignored.");
                        return;
                    }
                    DSIMobilityHorizonTarget.this.serviceInstancesDisable();
                }
            }
        };
        this.proxy.addServiceStateListener(class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizon == null ? (class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizon = DSIMobilityHorizonTarget.class$("org.dsi.ifc.mobilityhorizon.DSIMobilityHorizon")) : class$org$dsi$ifc$mobilityhorizon$DSIMobilityHorizon, dSIServiceStateListener);
    }

    protected void serviceInstancesDisable() {
        this.logger.trace("serviceInstancesDisable()");
        this.datapool.setServiceAvailable(false);
        for (DSIMobilityHorizonTargetData dSIMobilityHorizonTargetData : this.datapool.getServiceInstances().values()) {
            dSIMobilityHorizonTargetData.getDsiMobilityHorizonVW().setFacadeEnabled(false);
        }
        ASLNavigationMapFactory.getNavigationMapApi().sendEvMobilityHorizonServiceNotAvailable();
    }

    protected void serviceInstancesInit() {
        this.logger.trace("serviceInstancesInit()");
        this.datapool.setServiceAvailable(true);
        for (DSIMobilityHorizonTargetData dSIMobilityHorizonTargetData : this.datapool.getServiceInstances().values()) {
            this.initMobilityHorizonTarget(dSIMobilityHorizonTargetData);
        }
        ASLNavigationMapFactory.getNavigationMapApi().sendEvMobilityHorizonServiceAvailable();
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

