/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.dsi;

import org.dsi.ifc.organizer.AdbEntry;

public interface DSIAdbEditVW {
    public void changeEntry(AdbEntry var1, int var2);

    public void copyEntry(long var1);

    public void deleteEntries(long[] var1, int var2, int var3);

    public void deleteSpeedDial(int var1);

    public void getEntries(long[] var1, int var2, int var3);

    public void getEntryByReferenceId(String var1);

    public void getEntryDataSets(long[] var1, int var2, int var3);

    public void insertEntry(AdbEntry var1, int var2);

    public void setSpeedDial(AdbEntry var1);
}

