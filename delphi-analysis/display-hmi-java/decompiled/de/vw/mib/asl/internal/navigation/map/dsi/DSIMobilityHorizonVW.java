/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.dsi;

import org.dsi.ifc.mobilityhorizon.ConsumptionInfo;
import org.dsi.ifc.mobilityhorizon.MobilityHorizonLocation;

public interface DSIMobilityHorizonVW {
    public void setConsideredLocationTypes(int[] var1);

    public void setConsumptionInfo(ConsumptionInfo[] var1);

    public void setDriveTrainMode(int var1);

    public void setLocations(MobilityHorizonLocation[] var1);
}

