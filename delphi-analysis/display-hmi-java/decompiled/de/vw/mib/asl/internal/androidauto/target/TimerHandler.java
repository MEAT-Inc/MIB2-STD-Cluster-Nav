/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.androidauto.target;

import de.vw.mib.asl.framework.internal.framework.ServiceManager;
import de.vw.mib.asl.internal.androidauto.target.AndroidAutoTarget;
import de.vw.mib.asl.internal.androidauto.target.AudioHandler;
import de.vw.mib.asl.internal.androidauto.target.RequestHandler;
import de.vw.mib.genericevents.EventGeneric;
import de.vw.mib.timer.Timer;
import de.vw.mib.timer.TimerManager;

public class TimerHandler {
    AndroidAutoTarget target;
    AudioHandler audioHandler;
    RequestHandler requestHandler;
    private TimerManager timerManager;
    private Timer audioAnsweringDelayTimer;
    private Timer audioManagerTimeoutTimer;
    private Timer microphoneAnsweringDelayTimer;
    private Timer videoAvailableTimer;

    public TimerHandler(AndroidAutoTarget androidAutoTarget, AudioHandler audioHandler, RequestHandler requestHandler) {
        this.target = androidAutoTarget;
        this.audioHandler = audioHandler;
        this.requestHandler = requestHandler;
        this.timerManager = ServiceManager.timerManager;
        this.initializeAudioAnsweringDelayTimer();
        this.initializeAudioManagerTimeoutTimer();
        this.initializeMicrophoneAnsweringDelayTimer();
        this.initializeVideoAvailableTimer();
    }

    private void initializeAudioAnsweringDelayTimer() {
        if (this.target.isTraceEnabled()) {
            this.target.trace("TimerHandler::initializeAudioAnsweringDelayTimer");
        }
        this.audioAnsweringDelayTimer = this.timerManager.createTimer("AA_AUDIO_ANSWERING_DELAY_TIMER", 200L, false, new Runnable(){

            public void run() {
                if (TimerHandler.this.target.isTraceEnabled()) {
                    TimerHandler.this.target.trace("<< AA_AUDIO_ANSWERING_DELAY_TIMER expired... >>");
                }
                EventGeneric eventGeneric = ServiceManager.mGenericEventFactory.newEvent(100007);
                TimerHandler.this.target.sendSafe(eventGeneric);
            }
        }, Timer.TIMER_THREAD_INVOKER);
    }

    public void startAudioAnsweringDelayTimer() {
        if (this.target.isTraceEnabled()) {
            this.target.trace("TimerHandler::startAudioAnsweringDelayTimer");
        }
        if (!this.target.getTimerServer().isTimerActive(this.target.getTargetId(), 100007)) {
            this.target.startTimer(100007, 200L, false);
        }
    }

    public void stopAudioAnsweringDelayTimer() {
        if (this.target.isTraceEnabled()) {
            this.target.trace("TimerHandler::stopAudioAnsweringDelayTimer");
        }
        if (this.target.getTimerServer().isTimerActive(this.target.getTargetId(), 100007)) {
            this.target.stopTimer(100007);
        }
    }

    public boolean isAudioAnsweringDelayTimerStarted() {
        return this.audioAnsweringDelayTimer.isStarted();
    }

    private void initializeAudioManagerTimeoutTimer() {
        if (this.target.isTraceEnabled()) {
            this.target.trace("TimerHandler::initializeAudioManagerTimeoutTimer");
        }
        this.audioManagerTimeoutTimer = this.timerManager.createTimer("AA_AUDIO_MANAGER_TIMEOUT_TIMER", 5000L, false, new Runnable(){

            public void run() {
                if (TimerHandler.this.target.isTraceEnabled()) {
                    TimerHandler.this.target.trace("<< AA_AUDIO_MANAGER_TIMEOUT_TIMER expired... >>");
                }
                EventGeneric eventGeneric = ServiceManager.mGenericEventFactory.newEvent(100008);
                TimerHandler.this.target.sendSafe(eventGeneric);
            }
        }, Timer.TIMER_THREAD_INVOKER);
    }

    public void startAudioManagerTimeoutTimer() {
        if (this.target.isTraceEnabled()) {
            this.target.trace("TimerHandler::startAudioManagerTimeoutTimer");
        }
        if (!this.target.getTimerServer().isTimerActive(this.target.getTargetId(), 100008)) {
            this.target.startTimer(100008, 5000L, false);
        }
    }

    public void stopAudioManagerTimeoutTimer() {
        if (this.target.isTraceEnabled()) {
            this.target.trace("TimerHandler::stopAudioManagerTimeoutTimer");
        }
        if (this.target.getTimerServer().isTimerActive(this.target.getTargetId(), 100008)) {
            this.target.stopTimer(100008);
        }
    }

    public boolean isAudioManagerTimeoutTimerStarted() {
        return this.audioManagerTimeoutTimer.isStarted();
    }

    private void initializeMicrophoneAnsweringDelayTimer() {
        if (this.target.isTraceEnabled()) {
            this.target.trace("TimerHandler::initializeMicrophoneAnsweringDelayTimer");
        }
        this.microphoneAnsweringDelayTimer = this.timerManager.createTimer("AA_MICROPHONE_ANSWERING_DELAY_TIMER", 400L, false, new Runnable(){

            public void run() {
                if (TimerHandler.this.target.isTraceEnabled()) {
                    TimerHandler.this.target.trace("<< AA_MICROPHONE_ANSWERING_DELAY_TIMER expired... >>");
                }
                EventGeneric eventGeneric = ServiceManager.mGenericEventFactory.newEvent(100009);
                TimerHandler.this.target.sendSafe(eventGeneric);
            }
        }, Timer.TIMER_THREAD_INVOKER);
    }

    public void startMicrophoneAnsweringDelayTimer() {
        if (this.target.isTraceEnabled()) {
            this.target.trace("TimerHandler::startMicrophoneAnsweringDelayTimer");
        }
        if (!this.target.getTimerServer().isTimerActive(this.target.getTargetId(), 100009)) {
            this.target.startTimer(100009, 400L, false);
        }
    }

    public void stopMicrophoneAnsweringDelayTimer() {
        if (this.target.isTraceEnabled()) {
            this.target.trace("TimerHandler::stopMicrophoneAnsweringDelayTimer");
        }
        if (this.target.getTimerServer().isTimerActive(this.target.getTargetId(), 100009)) {
            this.target.stopTimer(100009);
        }
    }

    public boolean isMicrophoneAnsweringDelayTimerStarted() {
        return this.microphoneAnsweringDelayTimer.isStarted();
    }

    private void initializeVideoAvailableTimer() {
        if (this.target.isTraceEnabled()) {
            this.target.trace("TimerHandler::initializeVideoAvailableTimer");
        }
        this.videoAvailableTimer = this.timerManager.createTimer("AA_VIDEO_AVAILABLE_TIMER", 3000L, false, new Runnable(){

            public void run() {
                if (TimerHandler.this.target.isTraceEnabled()) {
                    TimerHandler.this.target.trace("<< AA_VIDEO_AVAILABLE_TIMER expired... >>");
                }
                EventGeneric eventGeneric = ServiceManager.mGenericEventFactory.newEvent(100010);
                TimerHandler.this.target.sendSafe(eventGeneric);
                TimerHandler.this.requestHandler.videoAvailableTimerExpired();
            }
        }, Timer.TIMER_THREAD_INVOKER);
    }

    public void startVideoAvailableTimer() {
        if (this.target.isTraceEnabled()) {
            this.target.trace("TimerHandler::startVideoAvailableTimer");
        }
        if (!this.target.getTimerServer().isTimerActive(this.target.getTargetId(), 100010)) {
            this.target.startTimer(100010, 3000L, false);
        }
    }

    public void stopVideoAvailableTimer() {
        if (this.target.isTraceEnabled()) {
            this.target.trace("TimerHandler::stopVideoAvailableTimer");
        }
        if (this.target.getTimerServer().isTimerActive(this.target.getTargetId(), 100010)) {
            this.target.stopTimer(100010);
        }
    }

    public boolean isVideoAvailableTimerStarted() {
        return this.target.getTimerServer().isTimerActive(this.target.getTargetId(), 100010);
    }
}

