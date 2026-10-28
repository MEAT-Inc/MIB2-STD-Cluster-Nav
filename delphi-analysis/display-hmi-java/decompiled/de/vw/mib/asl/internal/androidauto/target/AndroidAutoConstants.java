/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.androidauto.target;

public class AndroidAutoConstants {
    public static final int AUDIO_STATE_RELEASED = 0;
    public static final int AUDIO_STATE_REQUESTED = 1;
    public static final int AUDIO_STATE_CONNECTED = 2;
    public static final int ENTERTAINMENT_CONNECTION_STATE_TARGET_NOT_REGISTERED = 0;
    public static final int ENTERTAINMENT_CONNECTION_STATE_TARGET_REGISTER_REQUESTED = 1;
    public static final int ENTERTAINMENT_CONNECTION_STATE_TARGET_REGISTERED = 2;
    public static final int ENTERTAINMENT_CONNECTION_STATE_ENTERTAINMENT_REQUESTED = 3;
    public static final int ENTERTAINMENT_CONNECTION_STATE_AUDIO_REQUESTED = 4;
    public static final int ENTERTAINMENT_CONNECTION_STATE_READY = 5;
    public static final int AAP_AUDIO_FOCUS_REQUEST_UNKNOWN = 0;
    public static final int AAP_AUDIO_FOCUS_REQUEST_GAIN = 1;
    public static final int AAP_AUDIO_FOCUS_REQUEST_GAIN_TRANSIENT = 2;
    public static final int AAP_AUDIO_FOCUS_REQUEST_GAIN_TRANSIENT_MAY_DUCK = 3;
    public static final int AAP_AUDIO_FOCUS_REQUEST_RELEASE = 4;
    public static final String[] AAP_AUDIO_FOCUS_REQUEST = new String[]{"AAP_AUDIO_FOCUS_REQUEST_UNKNOWN", "AAP_AUDIO_FOCUS_REQUEST_GAIN", "AAP_AUDIO_FOCUS_REQUEST_GAIN_TRANSIENT", "AAP_AUDIO_FOCUS_REQUEST_GAIN_TRANSIENT_MAY_DUCK", "AAP_AUDIO_FOCUS_REQUEST_RELEASE"};
    public static final int AAP_AUDIO_FOCUS_NOTIFICATION_STATE_UNKNOWN = 0;
    public static final int AAP_AUDIO_FOCUS_NOTIFICATION_STATE_GAIN = 1;
    public static final int AAP_AUDIO_FOCUS_NOTIFICATION_STATE_GAIN_TRANSIENT_GUIDANCE_ONLY = 2;
    public static final int AAP_AUDIO_FOCUS_NOTIFICATION_STATE_GAIN_MEDIA_ONLY = 3;
    public static final int AAP_AUDIO_FOCUS_NOTIFICATION_STATE_LOSS_TRANSIENT_MAY_DUCK = 4;
    public static final int AAP_AUDIO_FOCUS_NOTIFICATION_STATE_LOSS = 5;
    public static final int AAP_AUDIO_FOCUS_NOTIFICATION_STATE_LOSS_TRANSIENT = 6;
    public static final int AAP_AUDIO_FOCUS_NOTIFICATION_STATE_NONE = 7;
    public static final String[] AAP_AUDIO_FOCUS_NOTIFICATION_STATE = new String[]{"AAP_AUDIO_FOCUS_NOTIFICATION_STATE_UNKNOWN", "AAP_AUDIO_FOCUS_NOTIFICATION_STATE_GAIN", "AAP_AUDIO_FOCUS_NOTIFICATION_STATE_GAIN_TRANSIENT_GUIDANCE_ONLY", "AAP_AUDIO_FOCUS_NOTIFICATION_STATE_GAIN_MEDIA_ONLY", "AAP_AUDIO_FOCUS_NOTIFICATION_STATE_LOSS_TRANSIENT_MAY_DUCK", "AAP_AUDIO_FOCUS_NOTIFICATION_STATE_LOSS", "AAP_AUDIO_FOCUS_NOTIFICATION_STATE_LOSS_TRANSIENT", "AAP_AUDIO_FOCUS_NOTIFICATION_STATE_NONE"};
    public static final String[] RESSOURCETRANSFERTYPE = new String[]{"UNKNOWN", "TAKE", "UNTAKE", "BORROW", "UNBORROW"};
    public static final String[] RESSOURCEOWNER = new String[]{"UNDEFINED", "MAINUNIT", "DEVICE"};
    public static final int HK_PTT_STATE_NONE = 0;
    public static final int HK_PTT_STATE_PRESSED = 1;
    public static final int HK_PTT_STATE_RELEASED = 2;
    public static final int HK_PTT_STATE_LONG_PRESSED = 3;
    public static final int HK_PTT_STATE_LONG_RELEASED = 4;
    public static final long MAX_TIMESTAMP_DELTA = 30000L;
    public static final long TIMER_50_MS = 50L;
    public static final long TIMER_100_MS = 100L;
    public static final long TIMER_200_MS = 200L;
    public static final long TIMER_300_MS = 300L;
    public static final long TIMER_400_MS = 400L;
    public static final long TIMER_3000_MS = 3000L;
    public static final long TIMER_5000_MS = 5000L;
    public static final boolean ANDROIDAUTO_NAVIGATION_ACTIVE = true;
    public static final boolean ANDROIDAUTO_NAVIGATION_INACTIVE = false;
    public static final int SENSOR_MODE_NIGHT = 2;
    public static final String[] VIDEOFOCUS_STATE = new String[]{"VIDEOFOCUS_UNKNOWN", "VIDEOFOCUS_PROJECTED", "VIDEOFOCUS_NATIVE"};
}

