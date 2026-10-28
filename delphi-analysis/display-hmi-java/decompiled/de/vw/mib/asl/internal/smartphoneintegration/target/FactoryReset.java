/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.smartphoneintegration.target;

import de.vw.mib.asl.api.system.ASLSystemAPI;
import de.vw.mib.asl.api.system.ASLSystemFactory;
import de.vw.mib.asl.api.system.factoryreset.FactoryResetCallback;
import de.vw.mib.asl.api.system.factoryreset.FactoryResetComponents;
import de.vw.mib.asl.api.system.factoryreset.FactoryResetParticipant;
import de.vw.mib.asl.internal.smartphoneintegration.common.SmartPhoneIntegrationGlobalProperyAccessor;
import de.vw.mib.asl.internal.smartphoneintegration.target.HsmTarget;

public class FactoryReset {
    ASLSystemAPI systemAPI = ASLSystemFactory.getSystemApi();
    FactoryResetParticipant frp;
    private HsmTarget target;
    String classname = "SmartPhoneIntegration.FactoryReset";

    public FactoryReset(final HsmTarget hsmTarget) {
        this.target = hsmTarget;
        this.frp = new FactoryResetParticipant(){

            public long getTimeout() {
                return 4000L;
            }

            public void reset(FactoryResetCallback factoryResetCallback, int n) {
                if (FactoryReset.this.getTarget().isTraceEnabled()) {
                    FactoryReset.this.getTarget().trace().append(FactoryReset.this.classname).append(".handle(reset) conn method=").append(SmartPhoneIntegrationGlobalProperyAccessor.getInstance().getCurrentConnectedDevice() != null ? new StringBuffer().append(SmartPhoneIntegrationGlobalProperyAccessor.getInstance().getCurrentConnectedDevice().getSelectedConnectionMethod()).append("").toString() : "none").log();
                }
                FactoryReset.this.getTarget().getPersistence().clear();
                if (SmartPhoneIntegrationGlobalProperyAccessor.getInstance().getCurrentConnectedDevice() != null && SmartPhoneIntegrationGlobalProperyAccessor.getInstance().getCurrentConnectedDevice().getSelectedConnectionMethod() != 1) {
                    FactoryReset.this.getGlobal().setMirrorlinkFactoryReset(true);
                } else {
                    hsmTarget.triggerObserver(6100020, null);
                    hsmTarget.getDSISmartphoneIntegration().disconnectDevice(SmartPhoneIntegrationGlobalProperyAccessor.getInstance().getCurrentConnectedDevice().getDeviceID());
                }
                FactoryReset.this.getTarget().getDSISmartphoneIntegration().requestFactorySettings(1);
                factoryResetCallback.notifyResetDone();
            }
        };
    }

    public void register() {
        this.systemAPI.getFactoryResetService().addParticipant(this.frp, FactoryResetComponents.APP_CONNECT);
    }

    public HsmTarget getTarget() {
        return this.target;
    }

    SmartPhoneIntegrationGlobalProperyAccessor getGlobal() {
        return SmartPhoneIntegrationGlobalProperyAccessor.getInstance();
    }
}

