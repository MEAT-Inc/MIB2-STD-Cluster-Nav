/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.androidauto.target;

import de.vw.mib.asl.api.system.ASLSystemFactory;
import de.vw.mib.asl.api.system.KeyAdapter;
import de.vw.mib.asl.internal.androidauto.target.AndroidAutoGlobalProperties;
import de.vw.mib.asl.internal.androidauto.target.AndroidAutoTarget;
import de.vw.mib.asl.internal.androidauto.target.SpeechHandler;
import de.vw.mib.asl.internal.androidauto.target.StartupHandler;

public class KeyHandler
extends KeyAdapter {
    AndroidAutoTarget target;
    AndroidAutoGlobalProperties properties;
    StartupHandler startupHandler;
    SpeechHandler speechHandler;

    public KeyHandler(AndroidAutoTarget androidAutoTarget, AndroidAutoGlobalProperties androidAutoGlobalProperties, StartupHandler startupHandler, SpeechHandler speechHandler) {
        this.target = androidAutoTarget;
        this.properties = androidAutoGlobalProperties;
        this.startupHandler = startupHandler;
        this.speechHandler = speechHandler;
        ASLSystemFactory.getSystemApi().addKeyListener(15, this);
    }

    public void onLongPressed(int n) {
        if (this.target.isTraceEnabled()) {
            this.target.trace("KeyHandler::onLongPressed - keyId = " + n);
        }
        this.properties.setHkPTTState(3);
        if (this.startupHandler.isDeviceConnected() && this.startupHandler.isDSI2Registered() && !this.properties.isGALSpeechActive()) {
            this.speechHandler.checkAndStartGALSpeech();
        }
    }

    public void onLongReleased(int n) {
        if (this.target.isTraceEnabled()) {
            this.target.trace("KeyHandler::onLongReleased - keyId = " + n);
        }
        this.properties.setHkPTTState(4);
        if (this.properties.isPTTPressedToStartGALSpeech()) {
            this.properties.setPTTPressedToStartGALSpeech(false);
        } else if (this.startupHandler.isDeviceConnected() && this.startupHandler.isDSI2Registered() && this.properties.isGALSpeechActive()) {
            this.target.getDSIAndroidAuto2().postButtonEvent(84, 1);
        }
    }

    public void onMultiPressed(int n) {
        if (this.target.isTraceEnabled()) {
            this.target.trace("KeyHandler::onMultiPressed - keyId = " + n);
        }
    }

    public void onPressed(int n) {
        if (this.target.isTraceEnabled()) {
            this.target.trace("KeyHandler::onPressed - keyId = " + n);
        }
        this.properties.setHkPTTState(1);
        if (this.startupHandler.isDeviceConnected() && this.startupHandler.isDSI2Registered() && this.properties.isGALSpeechActive()) {
            this.target.getDSIAndroidAuto2().postButtonEvent(84, 0);
        }
    }

    public void onReleased(int n) {
        if (this.target.isTraceEnabled()) {
            this.target.trace("KeyHandler::onReleased - keyId = " + n);
        }
        this.properties.setHkPTTState(2);
        if (this.startupHandler.isDeviceConnected() && this.startupHandler.isDSI2Registered() && this.properties.isGALSpeechActive()) {
            this.target.getDSIAndroidAuto2().postButtonEvent(84, 1);
        }
    }

    public void onUltraLongPressed(int n) {
        if (this.target.isTraceEnabled()) {
            this.target.trace("KeyHandler::onUltraLongPressed - keyId = " + n);
        }
    }
}

