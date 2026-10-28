/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.androidauto.target;

import de.vw.mib.asl.internal.androidauto.target.AndroidAutoGlobalProperties;
import de.vw.mib.asl.internal.androidauto.target.AndroidAutoTarget;
import de.vw.mib.asl.internal.androidauto.target.AudioHandler;
import de.vw.mib.asl.internal.androidauto.target.StartupHandler;
import de.vw.mib.dialogactivation.ActivationState;
import de.vw.mib.dialogactivation.SpeechDialogActivationAdmin;
import de.vw.mib.dialogactivation.SpeechDialogActivationApplicant;
import de.vw.mib.dialogactivation.internal.SpeechDialogActivationApplicantAdapter;
import org.osgi.framework.BundleContext;

public class SpeechHandler
extends SpeechDialogActivationApplicantAdapter {
    AndroidAutoTarget target;
    private AndroidAutoGlobalProperties properties;
    StartupHandler startupHandler;
    private AudioHandler audioHandler;
    private SpeechDialogActivationAdmin sdsAdmin;

    public SpeechHandler(AndroidAutoTarget androidAutoTarget, BundleContext bundleContext, AndroidAutoGlobalProperties androidAutoGlobalProperties, StartupHandler startupHandler, AudioHandler audioHandler) {
        super(bundleContext);
        this.target = androidAutoTarget;
        this.properties = androidAutoGlobalProperties;
        this.startupHandler = startupHandler;
        this.audioHandler = audioHandler;
        this.sdsAdmin = new NullSdsAdmin();
    }

    public void checkAndStartGALSpeech() {
        this.sdsAdmin.readActivationState(this);
    }

    public void resultReadActivationState(ActivationState activationState) {
        if (activationState.equals(ActivationState.INACTIVE)) {
            if (this.startupHandler.isDSI2Registered() && this.startupHandler.isDeviceConnected()) {
                this.target.getDSIAndroidAuto2().postButtonEvent(84, 0);
                this.target.getDSIAndroidAuto2().postButtonEvent(84, 1);
            }
            this.properties.setPTTPressedToStartGALSpeech(true);
        }
    }

    public void forceStartGALSpeech() {
        if (this.target.isTraceEnabled()) {
            this.target.trace("SpeechHandler::forceStartGALSpeech()");
        }
        this.sdsAdmin.forceActivationStateChange(ActivationState.ACTIVE, this);
        this.properties.setGALSpeechActive(true);
    }

    public void forceStopGALSpeech() {
        if (this.target.isTraceEnabled()) {
            this.target.trace("SpeechHandler::forceStopGALSpeech()");
        }
        this.sdsAdmin.forceActivationStateChange(ActivationState.INACTIVE, this);
        this.properties.setGALSpeechActive(false);
    }

    public void updateActivationState(ActivationState activationState) {
        if (this.target.isTraceEnabled()) {
            this.target.trace("SpeechHandler::updateActivationState( newstate = " + activationState + " )");
        }
        if (activationState == ActivationState.ACTIVE && (this.properties.getCurrentAudioFocusState() == 1 || this.properties.getCurrentAudioFocusState() == 7)) {
            if (this.properties.getAudioState_CL_ANN_AMP_GAL_LOWERING() != 0) {
                this.audioHandler.releaseSoundConnection(161);
            }
            this.audioHandler.handleNewAudioFocusState(5, true);
        }
    }

    public void cancelActivation() {
    }

    public void resultChangeActivationState(boolean bl, ActivationState activationState) {
        if (!bl || activationState.equals(ActivationState.ACTIVE)) {
            // empty if block
        }
    }

    public void setAdmin(SpeechDialogActivationAdmin speechDialogActivationAdmin) {
        this.sdsAdmin = speechDialogActivationAdmin != null ? speechDialogActivationAdmin : new NullSdsAdmin();
    }

    public void updateApplicantsCount(int n) {
        super.updateApplicantsCount(n);
    }

    public boolean isRegistered() {
        return super.isRegistered();
    }

    public void cancelRequest(int n) {
        if (this.target.isTraceEnabled()) {
            this.target.trace("SpeechHandler::cancelRequest() called...");
        }
        if (n == 0 && this.startupHandler.isDeviceConnected() && this.startupHandler.isDSI2Registered() && this.properties.isGALSpeechActive()) {
            this.target.getDSIAndroidAuto2().postButtonEvent(84, 0);
            this.target.getDSIAndroidAuto2().postButtonEvent(84, 1);
        }
    }

    public boolean isServiceRegistered() {
        return super.isServiceRegistered();
    }

    class NullSdsAdmin
    implements SpeechDialogActivationAdmin {
        NullSdsAdmin() {
        }

        public void changeActivationState(ActivationState activationState, SpeechDialogActivationApplicant speechDialogActivationApplicant) {
            this.handleNoSDSAdminAvailable();
        }

        public void forceActivationStateChange(ActivationState activationState, SpeechDialogActivationApplicant speechDialogActivationApplicant) {
            this.handleNoSDSAdminAvailable();
        }

        public void readActivationState(SpeechDialogActivationApplicant speechDialogActivationApplicant) {
            this.handleNoSDSAdminAvailable();
        }

        private void handleNoSDSAdminAvailable() {
            SpeechHandler.this.target.error("no SDSAdmin available, cannot start speech");
        }
    }
}

