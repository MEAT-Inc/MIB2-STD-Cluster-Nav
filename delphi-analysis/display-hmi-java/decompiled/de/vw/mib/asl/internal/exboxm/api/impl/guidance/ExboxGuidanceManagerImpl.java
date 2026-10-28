/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.exboxm.api.impl.guidance;

import de.vw.mib.asl.api.exboxm.guidance.ExboxGuidanceListener;
import de.vw.mib.asl.api.exboxm.guidance.ExboxGuidanceManager;
import de.vw.mib.asl.api.exboxm.guidance.GuidanceState;
import de.vw.mib.asl.internal.exboxm.state.ExboxStateService;
import de.vw.mib.asl.internal.exboxm.util.ExboxLogger;
import de.vw.mib.asl.internal.exboxm.util.Preconditions;
import de.vw.mib.genericevents.ThreadSwitchingTarget;
import de.vw.mib.log4mib.Logger;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;

public class ExboxGuidanceManagerImpl
implements ExboxGuidanceManager,
ExboxGuidanceListener {
    private final ExboxStateService exboxStateService;
    private final ExboxLogger exboxLogger;
    private final ThreadSwitchingTarget threadSwitchingTarget;
    private final Set listeners;

    public ExboxGuidanceManagerImpl(Logger logger, ExboxStateService exboxStateService, ThreadSwitchingTarget threadSwitchingTarget) {
        Preconditions.checkArgumentNotNull(logger, "EX: Logger must not be null!");
        Preconditions.checkArgumentNotNull(exboxStateService, "EX: ExboxStateService must not be null!");
        Preconditions.checkArgumentNotNull(threadSwitchingTarget, "EX: ThreadSwitchingTarget must not be null!");
        this.exboxLogger = new ExboxLogger(logger, this.getClass());
        this.exboxStateService = exboxStateService;
        this.exboxStateService.setGuidanceListener(this);
        this.threadSwitchingTarget = threadSwitchingTarget;
        this.listeners = new HashSet();
    }

    public void addListener(ExboxGuidanceListener exboxGuidanceListener) throws IllegalArgumentException {
        if (exboxGuidanceListener == null) {
            throw new IllegalArgumentException("EX: Incoming ExboxGuidanceListener instance is null!");
        }
        if (this.listeners.contains(exboxGuidanceListener)) {
            throw new IllegalArgumentException("EX: Incoming ExboxGuidanceListener instance is already registered!");
        }
        this.listeners.add(exboxGuidanceListener);
    }

    public void changeSmartphoneGuidanceStateTo(GuidanceState guidanceState) {
        this.exboxStateService.setSmartphoneGuidanceState(guidanceState);
    }

    public GuidanceState getGuidanceState() {
        return this.exboxStateService.getExboxGuidanceState();
    }

    public void onExboxGuidanceStateChanged(GuidanceState guidanceState) {
        this.notifyListeners(guidanceState);
    }

    public void removeListener(ExboxGuidanceListener exboxGuidanceListener) {
        this.listeners.remove(exboxGuidanceListener);
    }

    private void notifyListener(final ExboxGuidanceListener exboxGuidanceListener, final GuidanceState guidanceState) {
        this.threadSwitchingTarget.enqueue(new Runnable(){

            public void run() {
                exboxGuidanceListener.onExboxGuidanceStateChanged(guidanceState);
            }
        });
    }

    private void notifyListeners(GuidanceState guidanceState) {
        if (this.listeners.isEmpty()) {
            this.exboxLogger.warn("No instances of ExboxGuidanceListener registered.");
            return;
        }
        Iterator iterator = this.listeners.iterator();
        while (iterator.hasNext()) {
            ExboxGuidanceListener exboxGuidanceListener = (ExboxGuidanceListener)iterator.next();
            this.notifyListener(exboxGuidanceListener, guidanceState);
        }
    }
}

