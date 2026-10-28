/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.androidauto.target;

import de.vw.mib.asl.internal.androidauto.target.AndroidAutoTarget;
import de.vw.mib.asl.internal.androidauto.target.AudioHandler;
import de.vw.mib.asl.internal.androidauto.target.RequestHandler;

class DSIHandler {
    private AndroidAutoTarget target;
    private AudioHandler audioHandler;
    private RequestHandler requestHandler;

    DSIHandler(AndroidAutoTarget androidAutoTarget, AudioHandler audioHandler, RequestHandler requestHandler) {
        this.target = androidAutoTarget;
        this.audioHandler = audioHandler;
        this.requestHandler = requestHandler;
    }

    public void handleDsiAndroidAuto2VideoFocusRequestNotification(int n, int n2) {
        if (this.target.isTraceEnabled()) {
            this.target.trace("DSIHandler::handleDsiAndroidAuto2VideoFocusRequestNotification - validFlag      = " + n2);
            this.target.trace("DSIHandler::handleDsiAndroidAuto2VideoFocusRequestNotification - videoFocusMode = " + n);
        }
        if (n2 == 1) {
            this.requestHandler.performVideoFocusRequestNotification(n);
        }
    }

    public void handleDsiAndroidAuto2VideoAvailable(boolean bl, int n) {
        if (this.target.isTraceEnabled()) {
            this.target.trace("DSIHandler::handleDsiAndroidAuto2VideoFocusRequestNotification - validFlag      = " + n);
            this.target.trace("DSIHandler::handleDsiAndroidAuto2VideoFocusRequestNotification - videoAvailable = " + bl);
        }
        if (n == 1) {
            this.requestHandler.performVideoAvailable(bl);
        }
    }

    public void handleDsiAndroidAuto2AudioFocusRequestNotification(int n, int n2) {
        if (this.target.isTraceEnabled()) {
            this.target.trace("DSIHandler::handleDsiAndroidAuto2VideoFocusRequestNotification - validFlag             = " + n2);
            this.target.trace("DSIHandler::handleDsiAndroidAuto2VideoFocusRequestNotification - audioFocusRequestType = " + n);
        }
        if (n2 == 1) {
            this.requestHandler.performAudioFocusRequestNotification(n);
        }
    }

    public void handleDsiAndroidAuto2AudioAvailable(int n, boolean bl, int n2) {
        if (this.target.isTraceEnabled()) {
            this.target.trace("DSIHandler::handleDsiAndroidAuto2AudioAvailable - validFlag        = " + n2);
            this.target.trace("DSIHandler::handleDsiAndroidAuto2AudioAvailable - audioChannelType = " + n);
            this.target.trace("DSIHandler::handleDsiAndroidAuto2AudioAvailable - audioAvailable   = " + bl);
        }
        if (n2 == 1) {
            this.audioHandler.performAudioAvailable(n, bl);
        }
    }

    public void handleDsiAndroidAuto2VoiceSessionNotification(int n, int n2) {
        if (this.target.isTraceEnabled()) {
            this.target.trace("DSIHandler::handleDsiAndroidAuto2VoiceSessionNotification - validFlag          = " + n2);
            this.target.trace("DSIHandler::handleDsiAndroidAuto2VoiceSessionNotification - voiceSessionStatus = " + n);
        }
        if (n2 == 1) {
            this.requestHandler.performVoiceSessionNotification(n);
        }
    }

    public void handleDsiAndroidAuto2MicrophoneRequestNotification(int n, int n2) {
        if (this.target.isTraceEnabled()) {
            this.target.trace("DSIHandler::handleDsiAndroidAuto2MicrophoneRequestNotification - validFlag     = " + n2);
            this.target.trace("DSIHandler::handleDsiAndroidAuto2MicrophoneRequestNotification - micModeStatus = " + n);
        }
        if (n2 == 1) {
            this.requestHandler.performMicrophoneRequestNotification(n);
        }
    }

    public void handleDsiAndroidAuto2NavFocusRequestNotification(int n, int n2) {
        if (this.target.isTraceEnabled()) {
            this.target.trace("DSIHandler::handleDsiAndroidAuto2NavFocusRequestNotification - validFlag    = " + n2);
            this.target.trace("DSIHandler::handleDsiAndroidAuto2NavFocusRequestNotification - navFocusType = " + n);
        }
        if (n2 == 1) {
            this.requestHandler.performNavFocusRequestNotification(n);
        }
    }
}

