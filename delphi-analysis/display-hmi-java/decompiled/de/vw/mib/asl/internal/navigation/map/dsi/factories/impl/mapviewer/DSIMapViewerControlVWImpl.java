/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.mapviewer;

import de.vw.mib.asl.api.navigation.map.ASLNavigationMapFactory;
import de.vw.mib.asl.api.navigation.util.ASLNavigationUtilFactory;
import de.vw.mib.asl.api.navigation.util.IExtLogger;
import de.vw.mib.asl.framework.internal.framework.ServiceManager;
import de.vw.mib.asl.internal.navigation.map.GoogleEarthUtils;
import de.vw.mib.asl.internal.navigation.map.MapViewerUtils;
import de.vw.mib.asl.internal.navigation.map.dsi.DSIMapViewerControlVW;
import de.vw.mib.asl.internal.navigation.map.dsi.citymodel.CityModelService;
import de.vw.mib.asl.internal.navigation.map.dsi.datapool.MapDataPool;
import de.vw.mib.asl.internal.navigation.map.dsi.factories.DSIMapViewerControlFactoryVW;
import de.vw.mib.asl.internal.navigation.map.mainmap.MapViewerDatapoolShared;
import de.vw.mib.asl.internal.navigation.map.setup.PersistedMapSetup;
import de.vw.mib.genericevents.AbstractTarget;
import org.dsi.ifc.global.NavLocation;
import org.dsi.ifc.global.NavLocationWgs84;
import org.dsi.ifc.global.NavRectangle;
import org.dsi.ifc.map.DSIMapViewerControl;
import org.dsi.ifc.map.MapFlag;
import org.dsi.ifc.map.Point;
import org.dsi.ifc.map.Rect;

public class DSIMapViewerControlVWImpl
implements DSIMapViewerControlVW {
    private final IExtLogger LOGGER = ASLNavigationUtilFactory.getNavigationUtilApi().getExtLogger(65536, "[DSIMapViewerControlVWImpl]");
    private DSIMapViewerControl dsiMapViewerControl;
    private boolean facadeEnabled;
    private final MapDataPool mapDataPool;
    private final MapViewerDatapoolShared datapoolShared;
    private int instanceId;
    private final CityModelService cityModelService;
    private final boolean isHIGH = ServiceManager.configManagerDiag.isFeatureFlagSet(70);

    public DSIMapViewerControlVWImpl(MapDataPool mapDataPool) {
        this.mapDataPool = mapDataPool;
        this.datapoolShared = MapViewerDatapoolShared.getInstance();
        this.cityModelService = DSIMapViewerControlFactoryVW.getCityModelService();
    }

    public void configureFlags(int n, MapFlag[] mapFlagArray) {
        if (n == 0) {
            if (mapFlagArray != null && mapFlagArray.length > 0) {
                if (mapFlagArray[0].styleIndex == 23) {
                    mapFlagArray[0].handle = 200L;
                    this.LOGGER.trace("configureFlags(command=COMMAND_ADD home)");
                } else if (mapFlagArray[0].styleIndex == 28) {
                    this.LOGGER.trace("configureFlags(command=COMMAND_ADD favorite)");
                } else {
                    this.LOGGER.trace("configureFlags(command=COMMAND_ADD)");
                    int n2 = 300;
                    for (int i = 0; i < mapFlagArray.length; ++i) {
                        mapFlagArray[i].handle = n2;
                        ++n2;
                    }
                }
            }
        } else if (n == 1) {
            this.LOGGER.trace("configureFlags(command=COMMAND_CLEAR)");
        } else if (n == 2) {
            this.LOGGER.trace("configureFlags(command=COMMAND_REMOVE)");
        } else {
            this.LOGGER.makeWarn().append("configureFlags(command='").append("') - unsuported - NOT sending!").log();
            return;
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'configureFlags' will be ignored");
            return;
        }
        this.mapDataPool.setConfiguredFlags(mapFlagArray);
        this.dsiMapViewerControl.configureFlags(n, mapFlagArray);
    }

    public void dragMap(short s, short s2) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("dragMap(deltaX=").append(s).append(", deltaY=").append(s2).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'dragMap' will be ignored");
            return;
        }
        this.mapDataPool.setDragMapDeltaX(s);
        this.mapDataPool.setDragMapDeltaY(s2);
        this.dsiMapViewerControl.dragMap(s, s2);
    }

    public void dragRoute(short s, short s2) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("dragRoute(deltaX=").append(s).append(", deltaY=").append(s2).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'dragRoute' will be ignored");
            return;
        }
        this.mapDataPool.setDragRouteDeltaX(s);
        this.mapDataPool.setDragMapDeltaY(s2);
        this.dsiMapViewerControl.dragRoute(s, s2);
    }

    public void ehSetCategoryVisibility(int[] nArray, boolean[] blArray) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("ehSetCategoryVisibility(categoryUid.length=").append(nArray == null ? 0 : nArray.length).append(", visibility.length=").append(blArray == null ? 0 : blArray.length).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'ehSetCategoryVisibility' will be ignored");
            return;
        }
        this.mapDataPool.setEhCategoryVisibilityCategoryUIDs(nArray);
        this.mapDataPool.setEhCategoryVisibilityCategoryVisibility(blArray);
        if (this.isMapViewerCurrentGoogleEarth()) {
            DSIMapViewerControlFactoryVW.setEhCategoryVisibilityOnMapViewer(0, nArray, blArray);
        } else if (this.isMapViewerCurrentOnboard()) {
            DSIMapViewerControlFactoryVW.setEhCategoryVisibilityOnMapViewer(1, nArray, blArray);
        }
        if (this.isHIGH) {
            if (this.LOGGER.isTraceEnabled()) {
                this.LOGGER.makeTrace().append("Setting categories visibility on Kombi").log();
            }
            DSIMapViewerControlFactoryVW.setEhCategoryVisibilityOnMapViewer(3, nArray, blArray);
        }
        this.dsiMapViewerControl.ehSetCategoryVisibility(0, nArray, blArray);
        this.dsiMapViewerControl.ehSetCategoryVisibility(2, nArray, blArray);
    }

    public void ehSetCategoryVisibilityToDefault() {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("ehSetCategoryVisibilityToDefault()").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'ehSetCategoryVisibilityToDefault' will be ignored");
            return;
        }
        this.mapDataPool.setEhCategoryVisibilityCategoryUIDs(null);
        this.mapDataPool.setEhCategoryVisibilityCategoryVisibility(null);
        if (this.isMapViewerCurrentGoogleEarth()) {
            DSIMapViewerControlFactoryVW.setEhCategoryVisibilityOnMapViewer0ToDefault();
        }
        if (this.isHIGH) {
            if (this.LOGGER.isTraceEnabled()) {
                this.LOGGER.makeTrace().append("Sets default categories visibility on FPK").log();
            }
            DSIMapViewerControlFactoryVW.setEhCategoryVisibilityOnMapViewerToDefault(3);
        }
        this.dsiMapViewerControl.ehSetCategoryVisibilityToDefault(0);
        this.dsiMapViewerControl.ehSetCategoryVisibilityToDefault(2);
    }

    public void ensurePoiVisibility(NavLocation[] navLocationArray) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("ensurePoiVisibility(locations.length=").append(navLocationArray.length).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'ensurePoiVisibility' will be ignored");
            return;
        }
        this.dsiMapViewerControl.ensurePoiVisibility(navLocationArray);
    }

    public void ensureTMCVisibility(long l) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("ensureTMCVisibility(").append(l).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'ensureTMCVisibility' will be ignored");
            return;
        }
        this.mapDataPool.setEnsureTMCVisibilityMessageId(l);
        this.dsiMapViewerControl.ensureTMCVisibility(l);
    }

    public DSIMapViewerControl getDsiMapViewerControl() {
        return this.dsiMapViewerControl;
    }

    public void getInfoForScreenPosition(AbstractTarget abstractTarget, Point point) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("getInfoForScreenPosition(x=").append(point.xPos).append(", y=").append(point.yPos).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'getInfoForScreenPosition' will be ignored");
            return;
        }
        ASLNavigationMapFactory.getNavigationMapApi().sendEvMapMainGetInfoForScreenPosition(abstractTarget, point);
    }

    public int getInstanceId() {
        return this.instanceId;
    }

    public void goToTMCMessage(long l) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("goToTMCMessage(").append(l).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'goToTMCMessage' will be ignored");
            return;
        }
        this.mapDataPool.setGotToTMCMessageId(l);
        this.dsiMapViewerControl.goToTMCMessage(l);
    }

    private boolean isFacadeEnabled() {
        return this.facadeEnabled;
    }

    private boolean isKombiMapViewer() {
        if (this.instanceId == 3) {
            return true;
        }
        return this.instanceId == 4;
    }

    private boolean isMapViewerCurrentGoogleEarth() {
        if (this.instanceId == 1) {
            return true;
        }
        return this.instanceId == 4;
    }

    private boolean isMapViewerCurrentOnboard() {
        if (this.instanceId == 0) {
            return true;
        }
        if (this.instanceId == 3) {
            return true;
        }
        return this.instanceId == 2;
    }

    private boolean isMapViewerCurrentMainMap() {
        return this.instanceId == 0 || this.instanceId == 1;
    }

    public void rbSelectAlternativeRoute(int n) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("rbSelectAlternativeRoute(index=").append(n).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'rbSelectAlternativeRoute' will be ignored");
            return;
        }
        this.mapDataPool.setRbSelectAlternativeRouteIndex(n);
        this.dsiMapViewerControl.rbSelectAlternativeRoute(n);
    }

    public void set3DLandmarksVisible(boolean bl) {
        this.LOGGER.trace("set3DLandmarksInVisible()");
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'set3DLandmarksVisible' will be ignored");
            return;
        }
        if (this.isMapViewerCurrentGoogleEarth()) {
            this.LOGGER.trace("The call will be ignored, set3DLandmarksVisible( boolean visible ) is not implemented in the Google Earth MapViewer");
            return;
        }
        if (this.mapDataPool.isFeature3DLandmarksEnabled()) {
            this.mapDataPool.setLandmarks3DVisible(bl);
            this.dsiMapViewerControl.set3DLandmarksVisible(bl);
        } else {
            this.LOGGER.trace("the 3DLandmark feature is disabled for this variant");
        }
    }

    public void setBrandIconStyle(int[] nArray, int n) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("setBrandIconStyle(brandUid.length=").append(nArray).append(", brandIconStyle=").append(n).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setBrandIconStyle' will be ignored");
            return;
        }
        if (this.isMapViewerCurrentGoogleEarth()) {
            this.LOGGER.trace("The call will be ignored, setBrandIconStyle(int[] brandUid, int brandIconStyle) is not implemented in the Google Earth MapViewer");
            return;
        }
        this.mapDataPool.setBrandIconStyle(n);
        this.mapDataPool.setBrandIconUIDs(nArray);
        this.dsiMapViewerControl.setBrandIconStyle(nArray, n);
        if (this.isHIGH) {
            if (this.LOGGER.isTraceEnabled()) {
                this.LOGGER.makeTrace().append("Setting brand icon style on Kombi.").log();
            }
            DSIMapViewerControlFactoryVW.setBrandIconStyleOnMapViewer(3, nArray, n);
        }
    }

    public void setCarPosition(Point point) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("setCarPosition(screenCarPosition=").append(point.toString()).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setCarPosition' will be ignored");
            return;
        }
        this.mapDataPool.setCarPosition(point);
        this.dsiMapViewerControl.setCarPosition(point);
    }

    public void setCityModelMode(int n) {
        if (this.LOGGER.isTraceEnabled()) {
            if (n == 2) {
                this.LOGGER.trace("setCityModelModeEnhanced()");
            } else if (n == 0) {
                this.LOGGER.trace("setCityModelModeOff()");
            }
        }
        if (this.isMapViewerCurrentGoogleEarth()) {
            this.LOGGER.trace("The call will be ignored, setCityModelMode( int cityModelMode ) is not implemented in the Google Earth MapViewer");
            this.mapDataPool.setCityModelMode(n);
            return;
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setCityModelMode' will be ignored");
            this.mapDataPool.setCityModelMode(n);
            return;
        }
        this.cityModelService.setIntendedCityModelMode(n);
        this.mapDataPool.setCityModelMode(this.cityModelService.getActiveCityModelMode());
    }

    public void setDayView() {
        this.LOGGER.trace("setDayView()");
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setDayView' will be ignored");
            return;
        }
        this.mapDataPool.setNightView(false);
        this.dsiMapViewerControl.setDayView();
    }

    public void setDragRouteMarker(int n) {
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setDragRouteMarker' will be ignored");
            return;
        }
        this.mapDataPool.setDrageRouteMarker(n);
        this.dsiMapViewerControl.setDragRouteMarker(n);
    }

    public void setDsiMapViewerControl(DSIMapViewerControl dSIMapViewerControl) {
        this.dsiMapViewerControl = dSIMapViewerControl;
    }

    public void setEnableSoftJump(boolean bl) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("setEnableSoftJump(enable=").append(bl).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setEnableSoftJump' will be ignored");
            return;
        }
        this.mapDataPool.setSoftJumpEnabled(bl);
        this.dsiMapViewerControl.setEnableSoftJump(bl);
    }

    public void setEnableSoftTilt(boolean bl) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("setEnableSoftTilt(enabled=").append(bl).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setEnableSoftTilt' will be ignored");
            return;
        }
        this.mapDataPool.setSoftTiltEnalbed(bl);
        this.dsiMapViewerControl.setEnableSoftTilt(bl);
    }

    public void setEnableSoftZoom(boolean bl) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("setEnableSoftZoom(enabled=").append(bl).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setEnableSoftZoom' will be ignored");
            return;
        }
        this.mapDataPool.setSoftZoomEnabled(bl);
        this.dsiMapViewerControl.setEnableSoftZoom(bl);
    }

    public void setFacadeEnabled(boolean bl) {
        this.facadeEnabled = bl;
    }

    public void setGeneralPoiVisibility(boolean bl) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("setGeneralPoiVisibility(enable=").append(bl).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setGeneralPoiVisibility' will be ignored");
            return;
        }
        this.mapDataPool.setGeneralPOIVisibility(bl);
        if (this.isHIGH) {
            if (this.LOGGER.isTraceEnabled()) {
                this.LOGGER.makeTrace().append("Setting general POI visibility on Kombi.").log();
            }
            DSIMapViewerControlFactoryVW.setGeneralPoiVisibilityOnMapViewer(3, bl);
        }
        this.dsiMapViewerControl.setGeneralPoiVisibility(bl);
    }

    public void setHotPoint(Point point) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("setHotPoint(x=").append(point.xPos).append(", y=").append(point.yPos).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setHotPoint' will be ignored");
            return;
        }
        this.mapDataPool.setHotPoint(point);
        this.dsiMapViewerControl.setHotPoint(point);
    }

    public void setInstanceId(int n) {
        this.instanceId = n;
    }

    public void setLocation(int n, short s) {
        if (this.LOGGER.isTraceEnabled()) {
            if (n == 2) {
                this.LOGGER.trace("setLocationCar()");
            } else if (n == 3) {
                this.LOGGER.trace("setLocationDestination()");
            }
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setLocation' will be ignored");
            return;
        }
        if (n == 0) {
            this.mapDataPool.setLocationType(2);
        } else if (n == 1) {
            this.mapDataPool.setLocationType(3);
        }
        this.dsiMapViewerControl.setLocation(n, s);
    }

    public void setLocationByLocation(NavLocation navLocation) {
        this.LOGGER.trace("setLocationByLocation()");
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setLocationByLocation' will be ignored");
            return;
        }
        this.mapDataPool.setLocationType(1);
        this.dsiMapViewerControl.setLocationByLocation(navLocation);
    }

    public void setMapLayerVisible(int[] nArray) {
        this.LOGGER.trace("setMapLayerVisible()");
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setMapLayerVisible' will be ignored");
            return;
        }
        this.mapDataPool.setMapLayerVisible(nArray);
        this.dsiMapViewerControl.setMapLayerVisible(nArray);
    }

    public void setMapViewPortByLD(NavLocation navLocation, NavLocation navLocation2, int n) {
        this.LOGGER.trace("setMapViewPortByLD()");
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setMapViewPortByLD' will be ignored");
            return;
        }
        this.mapDataPool.setViewProtByLDLocationFirst(navLocation);
        this.mapDataPool.setViewPortByLDLocationSecond(navLocation2);
        this.dsiMapViewerControl.setMapViewPortByLD(navLocation, navLocation2, n);
    }

    public void setMapViewPortByWGS84Rectangle(NavRectangle navRectangle, int n) {
        this.LOGGER.trace("setMapViewPortByWGS84Rectangle()");
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setMapViewPortByWGS84Rectangle' will be ignored");
            return;
        }
        this.mapDataPool.setViewPortByWGS84NavRectangle(navRectangle);
        this.dsiMapViewerControl.setMapViewPortByWGS84Rectangle(navRectangle, n);
    }

    public void setMetricSystem(int n) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("setMetricSystem(newMetricSystem=").append(n).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setMetricSystem' will be ignored");
            return;
        }
        this.mapDataPool.setMetricSystem(n);
        this.LOGGER.trace("setMetricSystem() -  we don't notify the southside anymore about a unit change, because all MapViewer implementations showing a differen behavior");
    }

    public void setMobilityHorizonVisibility(boolean bl) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("setMobilityHorizonVisibility(visibility=").append(bl).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setMobilityHorizonVisibility' will be ignored");
            return;
        }
        if (this.isMapViewerCurrentGoogleEarth()) {
            this.LOGGER.trace("The call will be ignored, setMobilityHorizonVisibility() is not implemented in the Google Earth MapViewer");
            return;
        }
        this.mapDataPool.setMobilityHorzionVisible(bl);
        this.dsiMapViewerControl.setMobilityHorizonVisibility(bl);
    }

    public void setMobilityHorizonZoomMode(int n) {
        if (this.LOGGER.isTraceEnabled()) {
            if (n == 1) {
                this.LOGGER.trace("setMobilityHorizonZoomModeCarPos()");
            } else if (n == 0) {
                this.LOGGER.trace("setMobilityHorizonZoomModeHorizon()");
            } else if (n == 2) {
                this.LOGGER.trace("setMobilityHorizonZoomModeRoute()");
            }
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setMobilityHorizonZoomMode' will be ignored");
            return;
        }
        if (this.isMapViewerCurrentGoogleEarth()) {
            this.LOGGER.trace("The call will be ignored, setMobilityHorizonZoomMode() is not implemented in the Google Earth MapViewer");
            return;
        }
        this.mapDataPool.setMobilityHorizonZoomMode(n);
        this.dsiMapViewerControl.setMobilityHorizonZoomMode(n);
    }

    public void setMode(int n) {
        int n2;
        if (this.LOGGER.isTraceEnabled()) {
            if (n == 6) {
                this.LOGGER.trace("setModeAlternativeRouteMap()");
            } else if (n == 11) {
                this.LOGGER.trace("setModeAlternativeRouteMapDifferentColors()");
            } else if (n == 13) {
                this.LOGGER.trace("setModeCountryOverview()");
            } else if (n == 3) {
                this.LOGGER.trace("setModeCrosshairMap()");
            } else if (n == 9) {
                this.LOGGER.trace("setModeDestinationMap()");
            } else if (n == 2) {
                this.LOGGER.trace("setModeFreeMap()");
            } else if (n == 14) {
                this.LOGGER.trace("setModeMobilityHorizon()");
            } else if (n == 10) {
                this.LOGGER.trace("setModeOverviewMap()");
            } else if (n == 1) {
                this.LOGGER.trace("setModePositionMap()");
            }
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setMode' will be ignored");
            return;
        }
        if (this.isMapViewerCurrentGoogleEarth() && (n2 = PersistedMapSetup.getInstance().getMainMapContent()) == 0 && (n == 2 || n == 3)) {
            boolean bl = GoogleEarthUtils.isUseCrosshairMap();
            n = bl ? 3 : 2;
        }
        if (this.isKombiMapViewer() && n != 1) {
            if (this.LOGGER.isTraceEnabled()) {
                this.LOGGER.makeTrace().append("The map mode '").append(n).append("' will be ignored for the kombi mapviewer").log();
            }
            return;
        }
        this.mapDataPool.setMapMode(n);
        this.dsiMapViewerControl.setMode(n);
        if (this.isMapViewerCurrentMainMap()) {
            ASLNavigationMapFactory.getNavigationMapApi().sendEvMapMainMapModeChanged(n);
        }
    }

    public void setNightView() {
        this.LOGGER.trace("setNightView()");
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setNightView' will be ignored");
            return;
        }
        this.mapDataPool.setNightView(true);
        this.dsiMapViewerControl.setNightView();
    }

    public void setOrientation(int n, Point point) {
        if (this.LOGGER.isTraceEnabled()) {
            if (n == 0) {
                this.LOGGER.trace("setOrientationHeadingUp()");
            } else if (n == 2) {
                this.LOGGER.trace("setOrientationNorthUp()");
            }
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setOrientation' will be ignored");
            return;
        }
        this.mapDataPool.setOrientation(n);
        this.dsiMapViewerControl.setOrientation(n, point);
        if (this.isMapViewerCurrentMainMap()) {
            ASLNavigationMapFactory.getNavigationMapApi().sendEvMapMainOrientationChanged(n);
        }
    }

    public void setRotation(short s) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("setRotation(").append(s).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setRotation' will be ignored");
            return;
        }
        this.mapDataPool.setRotation(s);
        this.dsiMapViewerControl.setRotation(s);
    }

    public void setRouteColoringPolicy(int n) {
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setRouteColoringPolicy' will be ignored");
            return;
        }
        this.mapDataPool.setRouteColoringPolicy(n);
        this.dsiMapViewerControl.setRouteColoringPolicy(n);
    }

    public void setRouteVisibility(boolean bl) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("setRouteVisibility(visible=").append(bl).append(")").log();
        }
        this.mapDataPool.setRouteVisible(bl);
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setRouteVisibility' will be ignored");
            return;
        }
        this.dsiMapViewerControl.setRouteVisibility(bl);
    }

    public void setScreenViewport(Rect rect) {
        if (rect == null) {
            this.LOGGER.warn("The screen viewport is null, the call 'setScreenViewport' will be ignored");
            return;
        }
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("setScreenViewport(screenViewport=").append(rect.toString()).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setScreenViewport' will be ignored");
            return;
        }
        this.mapDataPool.setScreenViewport(rect);
        this.dsiMapViewerControl.viewSetScreenViewport(rect);
    }

    public void setScreenViewportMaximum(Rect rect) {
        if (rect == null) {
            this.LOGGER.warn("The screen viewport maximum is null, the call 'setScreenViewportMaximum' will be ignored");
            return;
        }
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("setScreenViewportMaximum(screenViewportMaximum=").append(rect.toString()).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setScreenViewportMaximum' will be ignored");
            return;
        }
        this.mapDataPool.setScreenViewportMaximum(rect);
        this.dsiMapViewerControl.viewSetScreenViewportMaximum(rect);
    }

    public void setTemperatureScale(int n) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("setTemperatureScale(temperatureScale=").append(n).append(")").log();
        }
        this.mapDataPool.setTemperatureScale(n);
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setTemperatureScale' will be ignored");
            return;
        }
        this.dsiMapViewerControl.setTemperatureScale(n);
    }

    public void setTrafficMapStyle(boolean bl) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("setTrafficMapStyle(").append(bl).append(")").log();
        }
        this.mapDataPool.setTrafficMapStyle(bl);
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setTrafficMapStyle' will be ignored");
            return;
        }
        if (this.isMapViewerCurrentGoogleEarth()) {
            this.LOGGER.trace("The call will be ignored, setTrafficMapStyle( boolean trafficMapStyleEnabled ) is not implemented in the Google Earth MapViewer");
            return;
        }
        this.dsiMapViewerControl.setTrafficMapStyle(bl);
    }

    public void setViewType(int n) {
        if (this.LOGGER.isTraceEnabled()) {
            if (n == 0) {
                this.LOGGER.trace("setViewType2D()");
            } else if (n == 3) {
                this.LOGGER.trace("setViewType3D()");
            } else if (n == 1) {
                this.LOGGER.trace("setViewTypeBirdview()");
            }
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setViewType' will be ignored");
            return;
        }
        this.mapDataPool.setViewType(n);
        this.dsiMapViewerControl.setViewType(n);
        if (this.isMapViewerCurrentMainMap()) {
            ASLNavigationMapFactory.getNavigationMapApi().sendEvMapMainViewTypeChanged(n);
        }
    }

    public void setZoomArea(Rect rect) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("setZoomArea(zoomArea=").append(rect.toString()).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setZoomArea' will be ignored");
            return;
        }
        this.mapDataPool.setZoomArea(rect);
        this.dsiMapViewerControl.setZoomArea(rect);
    }

    public void setZoomLevel(float f, int n) {
        int n2;
        int n3;
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("setZoomLevel(zoomLevel=").append(f).append(", zoomIndex=").append(n).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setZoomLevel' will be ignored");
            return;
        }
        boolean bl = MapViewerUtils.isMapModeZoomable(this.mapDataPool.getMapMode());
        if (!bl && this.instanceId != 3) {
            this.LOGGER.error("The current MapMode is not zoom able, the zoomLevel will not be changed!");
            return;
        }
        if (f == -1.0f) {
            this.mapDataPool.setZoomLevel(MapViewerUtils.calculateZoomLevelByZoomIndex(n));
        } else {
            this.mapDataPool.setZoomLevel(f);
        }
        if (n == -1) {
            this.mapDataPool.setZoomListIndex(MapViewerUtils.calculateZoomIndexByZoomLevel(f));
        } else {
            this.mapDataPool.setZoomListIndex(n);
        }
        if (this.isMapViewerCurrentGoogleEarth() && (n3 = PersistedMapSetup.getInstance().getMainMapContent()) == 0 && ((n2 = DSIMapViewerControlFactoryVW.getMapDatapoolMain().getMapMode()) == 3 || n2 == 2)) {
            boolean bl2 = GoogleEarthUtils.isUseCrosshairMap();
            if (bl2 && n2 == 2) {
                this.LOGGER.trace("GoogleEarth workaroud: In this zoomLevel we switch to CrosshairMap, instead of using FreeMap, to show an Crosshair for StreetView.");
                this.setMode(3);
            } else if (!bl2 && n2 == 3) {
                this.LOGGER.trace("GoogleEarth workaroud: In this zoomLevel we switch from CrosshairMap to FreeMap to disable the visible Crosshair.");
                this.setMode(2);
            }
        }
        this.dsiMapViewerControl.setZoomLevel(f, n);
    }

    public void showSpeedAndFlowCongestions(boolean bl) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("showSpeedAndFlowCongestions(visible=").append(bl).append(")").log();
        }
        this.mapDataPool.setShowSpeedAndFlowCongestions(bl);
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'showSpeedAndFlowCongestions' will be ignored");
            return;
        }
        this.dsiMapViewerControl.showSpeedAndFlowCongestions(bl);
    }

    public void showSpeedAndFlowFreeFlow(boolean bl) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("showSpeedAndFlowFreeFlow(visible=").append(bl).append(")").log();
        }
        this.mapDataPool.setShowSpeedAndFlowFreeFlow(bl);
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'showSpeedAndFlowFreeFlow' will be ignored");
            return;
        }
        this.dsiMapViewerControl.showSpeedAndFlowFreeFlow(bl);
    }

    public void setSpeedAndFlowRoadClass(int n) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("setSpeedAndFlowRoadClass(roadClass=").append(n).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'setSpeedAndFlowRoadClass' will be ignored");
            return;
        }
        this.mapDataPool.setSpeedAndFlowRoadClass(n);
        this.dsiMapViewerControl.setSpeedAndFlowRoadClass(n);
    }

    public void showTMCMessages(boolean bl) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("showTMCMessages(").append(bl).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'showTMCMessages' will be ignored");
            return;
        }
        this.mapDataPool.setShowTmcMessages(bl);
        this.dsiMapViewerControl.showTMCMessages(bl);
    }

    public void showTrafficEventListView(long[] lArray, boolean bl, boolean bl2) {
        this.LOGGER.trace("showTrafficEventListView()");
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'showTrafficEventListView' will be ignored");
            return;
        }
        this.dsiMapViewerControl.showTrafficEventListView(lArray, bl, bl2);
    }

    public void startRouteDragging(NavLocationWgs84 navLocationWgs84) {
        this.LOGGER.trace("startRouteDragging()");
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'startRouteDragging' will be ignored");
            return;
        }
        this.dsiMapViewerControl.startRouteDragging(navLocationWgs84);
    }

    public void stopScrollToDirection() {
        this.LOGGER.trace("stopScrollToDirection()");
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'stopScrollToDirection' will be ignored");
            return;
        }
        this.dsiMapViewerControl.stopScrollToDirection();
    }

    public void touchApproach(boolean bl) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("touchApproach(").append(bl).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'touchApproach' will be ignored");
            return;
        }
        if (this.isMapViewerCurrentGoogleEarth()) {
            this.LOGGER.trace("The call will be ignored, touchApproach() is not implemented in the Google Earth MapViewer");
        } else {
            this.dsiMapViewerControl.touchApproach(bl);
        }
    }

    public void viewFreeze(boolean bl) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("viewFreeze(").append(bl).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'viewFreeze' will be ignored");
            return;
        }
        this.mapDataPool.setViewFreeze(bl);
        this.dsiMapViewerControl.viewFreeze(bl);
    }

    public void viewSetVisible(boolean bl) {
        if (this.LOGGER.isTraceEnabled()) {
            this.LOGGER.makeTrace().append("viewSetVisible(").append(bl).append(")").log();
        }
        if (!this.isFacadeEnabled()) {
            this.LOGGER.warn("The MapViewer facade is currently disabled, the call 'viewSetVisible' will be ignored");
            return;
        }
        if (bl && this.datapoolShared.isSpeechRecognitionActive()) {
            this.LOGGER.warn("Speech is active, the call 'viewSetVisible' will be ignored");
            return;
        }
        this.mapDataPool.setViewVisible(bl);
        this.dsiMapViewerControl.viewSetVisible(bl);
    }
}

