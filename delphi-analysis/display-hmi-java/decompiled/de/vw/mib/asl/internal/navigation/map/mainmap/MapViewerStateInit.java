/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.mainmap;

import de.vw.mib.asl.api.navigation.map.ASLNavigationMapFactory;
import de.vw.mib.asl.api.navigation.util.ASLNavigationUtilFactory;
import de.vw.mib.asl.api.navigation.util.IExtLogger;
import de.vw.mib.asl.api.speechengine.SpeechEngine;
import de.vw.mib.asl.api.speechengine.messenger.dialog.DialogStateConsumer;
import de.vw.mib.asl.framework.api.framework.ASLFrameworkFactory;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.DSIMapViewerControlFactoryVW;
import de.vw.mib.asl.internal.navigation.map.mainmap.MapViewerTargetHSM;
import de.vw.mib.genericevents.EventGeneric;
import de.vw.mib.genericevents.hsm.AbstractHsmState;
import de.vw.mib.genericevents.hsm.Hsm;
import de.vw.mib.genericevents.hsm.HsmState;
import org.dsi.ifc.global.NavLocation;
import org.osgi.framework.BundleContext;
import org.osgi.framework.ServiceReference;
import org.osgi.util.tracker.ServiceTracker;
import org.osgi.util.tracker.ServiceTrackerCustomizer;

public final class MapViewerStateInit
extends AbstractHsmState {
    private static final int[] ASL_OBSERVER = new int[]{1073742420, 1073742422, 1073744665, 1073742415, 3499051, 1074841951, 1074841955, 3499063, 3499064, 1073744564};
    private static final int[] ASL_SERVICES = new int[]{3499036, 3499051, 3499071};
    private static final int[] ATTRIBUTES_MAPVIEWER_CONTROL = new int[]{12, 11, 9, 10, 13};
    private final IExtLogger logger = ASLNavigationUtilFactory.getNavigationUtilApi().getExtLogger(65536, "[MapViewerStateInit]");
    private final MapViewerTargetHSM target;
    static /* synthetic */ Class class$de$vw$mib$asl$api$speechengine$SpeechEngine;

    public MapViewerStateInit(MapViewerTargetHSM mapViewerTargetHSM, Hsm hsm, String string, HsmState hsmState) {
        super(hsm, string, hsmState);
        this.target = mapViewerTargetHSM;
    }

    public HsmState handle(EventGeneric eventGeneric) throws Exception {
        switch (eventGeneric.getReceiverEventId()) {
            case 2: {
                this.handleEntry();
                break;
            }
            case 4: {
                this.handleExit();
                break;
            }
            case 3: {
                this.handleStart();
                break;
            }
            case 101001: {
                this.handleNaviTargetGoOn();
                break;
            }
            default: {
                this.handleDefault(eventGeneric);
                return this.myParent;
            }
        }
        return null;
    }

    private void handleDefault(EventGeneric eventGeneric) {
        if (this.logger.isTraceEnabled()) {
            this.logger.makeTrace().append("handle(): DEFAULT ev.Id=").append(eventGeneric.getReceiverEventId()).append(",Params=").append(eventGeneric.getParamString()).log();
        }
    }

    private void handleEntry() {
        this.logger.trace("handleEntry()");
    }

    private void handleExit() {
        this.logger.trace("handleExit()");
    }

    private void handleNaviTargetGoOn() throws Exception {
        this.logger.trace("handleNaviTargetGoOn()");
        this.initDSI();
        this.initASL();
        this.initSpeechEngine();
        this.target.transStateWork();
    }

    private void handleStart() throws Exception {
        this.logger.trace("handleStart()");
        this.target.registerServices(ASL_SERVICES, false);
    }

    private void initASL() {
        this.target.addObservers(ASL_OBSERVER);
        NavLocation navLocation = this.target.datapool.getDefaultLocation();
        if (navLocation == null) {
            this.logger.trace("Map-Viewer: Init: Default location was still null.");
            return;
        }
        this.target.datapool.setMapPosition(navLocation);
    }

    private void initDSI() throws Exception {
        this.logger.trace("initDSI()");
        this.target.notifierDSI.setDsiMapViewerControl(DSIMapViewerControlFactoryVW.createMapViewerMain(this.target, ATTRIBUTES_MAPVIEWER_CONTROL));
    }

    private void initSpeechEngine() {
        final BundleContext bundleContext = ASLFrameworkFactory.getASLFrameworkAPI().getServices().getBundleContext();
        final DialogStateConsumer dialogStateConsumer = new DialogStateConsumer(){

            public void onDialogStateChanged(int n) {
                if (n == 0) {
                    ASLNavigationMapFactory.getNavigationMapApi().sendEvMapMainSpeechRecognizerActive();
                    ((MapViewerStateInit)MapViewerStateInit.this).target.datapoolShared.setSpeechRecognitionActive(true);
                }
                if (n == 1) {
                    ASLNavigationMapFactory.getNavigationMapApi().sendEvMapMainSpeechRecognizerInactive();
                    ((MapViewerStateInit)MapViewerStateInit.this).target.datapoolShared.setSpeechRecognitionActive(false);
                }
                if (n == 2) {
                    MapViewerStateInit.this.logger.trace("Speech active");
                    ((MapViewerStateInit)MapViewerStateInit.this).target.datapool.setSpeechActive(true);
                }
                if (n == 8) {
                    MapViewerStateInit.this.logger.trace("Speech inactive");
                    ((MapViewerStateInit)MapViewerStateInit.this).target.datapool.setSpeechActive(false);
                }
            }
        };
        ServiceTracker serviceTracker = new ServiceTracker(bundleContext, (class$de$vw$mib$asl$api$speechengine$SpeechEngine == null ? (class$de$vw$mib$asl$api$speechengine$SpeechEngine = MapViewerStateInit.class$("de.vw.mib.asl.api.speechengine.SpeechEngine")) : class$de$vw$mib$asl$api$speechengine$SpeechEngine).getName(), new ServiceTrackerCustomizer(){

            public Object addingService(ServiceReference serviceReference) {
                SpeechEngine speechEngine = (SpeechEngine)bundleContext.getService(serviceReference);
                speechEngine.getDialogStateRouter().register(dialogStateConsumer);
                return speechEngine;
            }

            public void modifiedService(ServiceReference serviceReference, Object object) {
            }

            public void removedService(ServiceReference serviceReference, Object object) {
            }
        });
        serviceTracker.open();
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

