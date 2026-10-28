/*
 * Decompiled with CFR 0.152.
 */
package de.vw.mib.asl.internal.navigation.map.dsi.factories.impl.navigation;

import de.vw.mib.asl.api.navigation.util.ASLNavigationUtilFactory;
import de.vw.mib.asl.api.navigation.util.IExtLogger;
import de.vw.mib.asl.internal.navigation.map.dsi.DSINavigationVW;
import org.dsi.ifc.base.DSIListener;
import org.dsi.ifc.global.NavLocation;
import org.dsi.ifc.global.NavLocationWgs84;
import org.dsi.ifc.global.NavSegmentID;
import org.dsi.ifc.navigation.DSINavigation;
import org.dsi.ifc.navigation.LIExtData;
import org.dsi.ifc.navigation.LISpellerData;
import org.dsi.ifc.navigation.NavLastDest;
import org.dsi.ifc.navigation.NavPoiInfoConfiguration;
import org.dsi.ifc.navigation.Route;
import org.dsi.ifc.navigation.RouteOptions;
import org.dsi.ifc.navigation.TryBestMatchData;
import org.dsi.ifc.navigation.TryMatchLocationData;

public class DSINavigationVWImpl
implements DSINavigationVW {
    private DSINavigation dsiNavigation;
    private boolean facadeEnabled;
    private final IExtLogger logger = ASLNavigationUtilFactory.getNavigationUtilApi().getExtLogger(65536, "[DSINavigationVWImpl]");

    public void afaRepeat(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("afaRepeat( int source )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.afaRepeat(n);
    }

    public void clearNotification(DSIListener dSIListener) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("clearNotification( DSIListener listener )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.clearNotification(dSIListener);
    }

    public void clearNotification(int n, DSIListener dSIListener) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("clearNotification( int attribute, DSIListener listener )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.clearNotification(n, dSIListener);
    }

    public void clearNotification(int[] nArray, DSIListener dSIListener) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("clearNotification( int[] attributes, DSIListener listener )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.clearNotification(nArray, dSIListener);
    }

    public void createExportFile(String string, int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("createExportFile( String file, int userID )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.createExportFile(string, n);
    }

    public void createNavLocationOfPOIUID(long l) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("createNavLocationOfPOIUID( long poiUid )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.createNavLocationOfPOIUID(l);
    }

    public void deletePersonalPOIDataBases(String[] stringArray) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("deletePersonalPOIDataBases( String[] paths )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.deletePersonalPOIDataBases(stringArray);
    }

    public void dmFlagDestinationRemove() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("dmFlagDestinationRemove()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.dmFlagDestinationRemove();
    }

    public void dmFlagDestinationSet(NavLocation navLocation) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("dmFlagDestinationSet( NavLocation location )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.dmFlagDestinationSet(navLocation);
    }

    public void dmFlagDestinationSetName(String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("dmFlagDestinationSetName( String name )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.dmFlagDestinationSetName(string);
    }

    public void dmLastDestinationsAddList(NavLastDest[] navLastDestArray) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("dmLastDestinationsAddList( NavLastDest[] lastDestList )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.dmLastDestinationsAddList(navLastDestArray);
    }

    public void dmLastDestinationsDelete(long l) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("dmLastDestinationsDelete( long destID )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.dmLastDestinationsDelete(l);
    }

    public void dmLastDestinationsDeleteAll() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("dmLastDestinationsDeleteAll()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.dmLastDestinationsDeleteAll();
    }

    public void dmLastDestinationsGet(long l) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("dmLastDestinationsGet( long idestID )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.dmLastDestinationsGet(l);
    }

    public void dmLastDestinationsReplace(long l, NavLocation navLocation, String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("dmLastDestinationsReplace( long destID, NavLocation destination, String title )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.dmLastDestinationsReplace(l, navLocation, string);
    }

    public void dmRecentRoutesAdd(Route route, String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("dmRecentRoutesAdd( Route route, String title )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.dmRecentRoutesAdd(route, string);
    }

    public void dmRecentRoutesDelete(long l) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("dmRecentRoutesDelete( long routeID )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.dmRecentRoutesDelete(l);
    }

    public void dmRecentRoutesDeleteAll() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("dmRecentRoutesDeleteAll()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.dmRecentRoutesDeleteAll();
    }

    public void dmRecentRoutesGet(long l) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("dmRecentRoutesGet( long routeID )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.dmRecentRoutesGet(l);
    }

    public void dmRecentRoutesReplace(long l, Route route, String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("dmRecentRoutesReplace( long routeID, Route route, String title )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.dmRecentRoutesReplace(l, route, string);
    }

    public void ehGetAllBrandsOfCategory(int n, int n2) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("ehGetAllBrandsOfCategory( int mapStyleType, int categoryUid )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.ehGetAllBrandsOfCategory(n, n2);
    }

    public void ehGetAllCategories(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("ehGetAllCategories( int mapStyleType )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.ehGetAllCategories(n);
    }

    public void ehSetBrandPreference(int n, int[] nArray, boolean[] blArray) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("ehSetBrandPreference( int mapStyleType, int[] brandUid, boolean[] preference )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.ehSetBrandPreference(n, nArray, blArray);
    }

    public void ehSetBrandVisibility(int n, int[] nArray, boolean[] blArray) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("ehSetBrandVisibility( int mapStyleType, int[] brandUid, boolean[] visibility )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.ehSetBrandVisibility(n, nArray, blArray);
    }

    public void ehSetCategoryAudioWarning(int n, int[] nArray, boolean[] blArray) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("ehSetCategoryAudioWarning( int mapStyleType, int[] categoryUid, boolean[] audible )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.ehSetCategoryAudioWarning(n, nArray, blArray);
    }

    public void ehSetCategoryMonitoring(int[] nArray, boolean[] blArray) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("ehSetCategoryMonitoring( int[] categoryUid, boolean[] monitor )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.ehSetCategoryMonitoring(nArray, blArray);
    }

    public void ehSetCategoryVisibility(int n, int[] nArray, boolean[] blArray) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("ehSetCategoryVisibility( int mapStyleType, int[] categoryUid, boolean[] visibility )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.ehSetCategoryVisibility(n, nArray, blArray);
    }

    public void ehSetCategoryVisibilityToDefault(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("ehSetCategoryVisibilityToDefault( int mapStyleType )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.ehSetCategoryVisibilityToDefault(n);
    }

    public void enableRgLaneGuidance(boolean bl) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("enableRgLaneGuidance( boolean enabled )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.enableRgLaneGuidance(bl);
    }

    public void enableRgMotorwayInfo(boolean bl) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("enableRgMotorwayInfo( boolean enable )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.setVirtualRouteGuidance(bl);
    }

    public void enableRgPoiInfo(boolean bl) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("enableRgPoiInfo( boolean enabled )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.enableRgPoiInfo(bl);
    }

    public void enableRgStreetLists(boolean bl) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("enableRgStreetLists( boolean enabled )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.enableRgStreetLists(bl);
    }

    public void etcGetCountryAbbreviation(String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("etcGetCountryAbbreviation( String country )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.etcGetCountryAbbreviation(string);
    }

    public void etcGetPositionTimeInfo(NavLocationWgs84 navLocationWgs84) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("etcGetPositionTimeInfo( NavLocationWgs84 position )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.etcGetPositionTimeInfo(navLocationWgs84);
    }

    public void etcSelectDatabase(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("etcSelectDatabase( int index )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.etcSelectDatabase(n);
    }

    public void etcSelectNavDataBase(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("etcSelectNavDataBase( int uid )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.etcSelectNavDataBase(n);
    }

    public void etcSetDemoMode(boolean bl) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("etcSetDemoMode( boolean enable )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.etcSetDemoMode(bl);
    }

    public void etcSetDemoModeSpeed(long l) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("etcSetDemoModeSpeed( long speed )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.etcSetDemoModeSpeed(l);
    }

    public void etcSetMetricSystem(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("etcSetMetricSystem( int metricSystem )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.etcSetMetricSystem(n);
    }

    public void etcTriggerNavigationRestart(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("etcTriggerNavigationRestart( int reason )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.etcTriggerNavigationRestart(n);
    }

    public void importFile(String string, int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("importFile( String file, int userID )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.importFile(string, n);
    }

    public void importRouteFromGpxFile(String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("importRouteFromGpxFile( String fileName )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.importRouteFromGpxFile(string);
    }

    public void jumpToNextManeuver() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("jumpToNextManeuver()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.jumpToNextManeuver();
    }

    public void languageSpellableCharacters(String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("languageSpellableCharacters( String countryAbbreviation )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.languageSpellableCharacters(string);
    }

    public void liDeleteHistory() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liDeleteHistory()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liDeleteHistory();
    }

    public void liDisambiguateLocation(NavLocation navLocation) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liDisambiguateLocation( NavLocation location )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liDisambiguateLocation(navLocation);
    }

    public void liGetCurrentState() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liGetCurrentState()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liGetCurrentState();
    }

    public void liGetLastCityHistoryEntry(long l) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liGetLastCityHistoryEntry( long id )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liGetLastCityHistoryEntry(l);
    }

    public void liGetLastStateHistoryEntry(long l) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liGetLastStateHistoryEntry( long id )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liGetLastStateHistoryEntry(l);
    }

    public void liGetLastStreetHistoryEntry(long l) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liGetLastStreetHistoryEntry( long id )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liGetLastStreetHistoryEntry(l);
    }

    public void liGetLocationDescriptionTransform(NavLocation navLocation) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liGetLocationDescriptionTransform( NavLocation location )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liGetLocationDescriptionTransform(navLocation);
    }

    public void liGetLocationDescriptionTransformNearBy(NavLocation navLocation) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liGetLocationDescriptionTransformNearBy( NavLocation location )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liGetLocationDescriptionTransformNearBy(navLocation);
    }

    public void liGetSpellableCharacters(NavLocation navLocation, int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liGetSpellableCharacters( NavLocation navLocation, int selectionCriterion )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liGetSpellableCharacters(navLocation, n);
    }

    public void liGetState() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liGetState()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liGetState();
    }

    public void liGetViaPointCountryList() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liGetViaPointCountryList()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liGetViaPointCountryList();
    }

    public void liGetViaPointList(int n, int n2, int n3, int n4) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liGetViaPointList( int windowSize, int offset, int anchorId, int openedListAnchorId )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liGetViaPointList(n, n2, n3, n4);
    }

    public void liHistoryAddLocation(NavLocation navLocation) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liHistoryAddLocation( NavLocation location )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liHistoryAddLocation(navLocation);
    }

    public void liLastCityHistoryAdd(NavLocation navLocation, boolean bl, String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liLastCityHistoryAdd( NavLocation city, boolean hasStreets, String nameofEntry )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liLastCityHistoryAdd(navLocation, bl, string);
    }

    public void liLastCityHistoryAddExtended(NavLocation navLocation, boolean bl, String string, LIExtData[] lIExtDataArray) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liLastCityHistoryAddExtended( NavLocation city, boolean hasStreets, String nameofEntry, LIExtData[] extendedData )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liLastCityHistoryAddExtended(navLocation, bl, string, lIExtDataArray);
    }

    public void liLastCityHistoryDelete(long l) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liLastCityHistoryDelete( long id )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liLastCityHistoryDelete(l);
    }

    public void liLastCityHistoryDeleteAll() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liLastCityHistoryDeleteAll()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liLastCityHistoryDeleteAll();
    }

    public void liLastCityHistorySetStreet(NavLocation navLocation) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liLastCityHistorySetStreet( NavLocation street ").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liLastCityHistorySetStreet(navLocation);
    }

    public void liLastStateHistoryAdd(NavLocation navLocation, boolean bl, String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liLastStateHistoryAdd( NavLocation state, boolean hasCities, String nameofEntry )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liLastStateHistoryAdd(navLocation, bl, string);
    }

    public void liLastStateHistoryAddExtended(NavLocation navLocation, boolean bl, String string, LIExtData[] lIExtDataArray) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liLastStateHistoryAddExtended( NavLocation state, boolean hasCities, String nameofEntry, LIExtData[] extendedData )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liLastStateHistoryAddExtended(navLocation, bl, string, lIExtDataArray);
    }

    public void liLastStateHistoryDelete(long l) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liLastStateHistoryDelete( long id )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liLastStateHistoryDelete(l);
    }

    public void liLastStateHistoryDeleteAll() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liLastStateHistoryDeleteAll()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liLastStateHistoryDeleteAll();
    }

    public void liLastStreetHistoryAdd(NavLocation navLocation, String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liLastStreetHistoryAdd( NavLocation street, String nameOfEntry )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liLastStreetHistoryAdd(navLocation, string);
    }

    public void liLastStreetHistoryAddExtended(NavLocation navLocation, String string, LIExtData[] lIExtDataArray) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liLastStreetHistoryAddExtended( NavLocation street, String nameofEntry, LIExtData[] extendedData )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liLastStreetHistoryAddExtended(navLocation, string, lIExtDataArray);
    }

    public void liLastStreetHistoryDelete(long l) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liLastStreetHistoryDelete( long id )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liLastStreetHistoryDelete(l);
    }

    public void liLastStreetHistoryDeleteAll() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liLastStreetHistoryDeleteAll()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liLastStreetHistoryDeleteAll();
    }

    public void liLastStreetHistorySetCity(NavLocation navLocation) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liLastStreetHistorySetCity( NavLocation city )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liLastStreetHistorySetCity(navLocation);
    }

    public void liRestoreState(LISpellerData lISpellerData) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liRestoreState( LISpellerData spellerState )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liRestoreState(lISpellerData);
    }

    public void liSelectViaPoint(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liSelectViaPoint( int viaPointId )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liSelectViaPoint(n);
    }

    public void liSetCountryForCityAndStreetHistory(String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liSetCountryForCityAndStreetHistory( String countryAbbreviation )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liSetCountryForCityAndStreetHistory(string);
    }

    public void liSetCurrentLD(NavLocation navLocation) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liSetCurrentLD( NavLocation locDescID )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liSetCurrentLD(navLocation);
    }

    public void liSetHistory(String string, String string2) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liSetHistory( String countryAbbreviation, String stateAbbreviation )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liSetHistory(string, string2);
    }

    public void liSetNVCRange(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liSetNVCRange( int nvcRange )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liSetNVCRange(n);
    }

    public void liSetStreetForCityHistory(String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liSetStreetForCityHistory( String street )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liSetStreetForCityHistory(string);
    }

    public void liSetViaPointCountry(String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liSetViaPointCountry( String countryAbbreviation )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liSetViaPointCountry(string);
    }

    public void lispAddCharacter(String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("lispAddCharacter( String inputChar )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.lispAddCharacter(string);
    }

    public void lispAddStroke(String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("lispAddStroke( String stroke )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.lispAddStroke(string);
    }

    public void lispCancelSpeller() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("lispCancelSpeller()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.lispCancelSpeller();
    }

    public void lispDeleteAllCharacters() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("lispDeleteAllCharacters()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.lispDeleteAllCharacters();
    }

    public void lispGetLocationFromLiValueListElement(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("lispGetLocationFromLiValueListElement( int listIndex )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.lispGetLocationFromLiValueListElement(n);
    }

    public void lispGetMatchingNVC(String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("lispGetMatchingNVC( String guessNVC )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.lispGetMatchingNVC(string);
    }

    public void lispRequestNVCList(int n, int n2, int n3) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("lispRequestNVCList( int nvcRange, int offset, int windowSize )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.lispRequestNVCList(n, n2, n3);
    }

    public void lispRequestValueListByListIndex(int n, boolean bl) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("lispRequestValueListByListIndex( int anchorIndex, boolean nextPage )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.lispRequestValueListByListIndex(n, bl);
    }

    public void lispSelectByCategoryUid(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("lispSelectByCategoryUid( int categoryUid )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.lispSelectByCategoryUid(n);
    }

    public void lispSelectByMultipleCategoryUids(int[] nArray) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("lispSelectByMultipleCategoryUids( int[] categoryUids )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.lispSelectByMultipleCategoryUids(nArray);
    }

    public void lispSelectItemFromLocation(NavLocation navLocation) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("lispSelectItemFromLocation( NavLocation historyLocation )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.lispSelectItemFromLocation(navLocation);
    }

    public void lispSelectListItem(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("lispSelectListItem( int index )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.lispSelectListItem(n);
    }

    public void lispSelectListItemByIdent(String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("lispSelectListItemByIdent( String ident )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.lispSelectListItemByIdent(string);
    }

    public void lispSetInput(String string, boolean bl) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("lispSetInput( String input, boolean autoSelectInput )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.lispSetInput(string, bl);
    }

    public void lispUndoCharacter() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("lispUndoCharacter()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.lispUndoCharacter();
    }

    public void liStartMultiCriteriaSpeller(int n, int n2, boolean bl, boolean bl2, boolean bl3) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liStartMultiCriteriaSpeller( int criterion1, int criterion2, boolean removeZipCode, boolean removeTown, boolean removeStreet )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liStartMultiCriteriaSpeller(n, n2, bl, bl2, bl3);
    }

    public void liStartSpeller(int n, boolean bl, boolean bl2, boolean bl3) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liStartSpeller( int selectionCriterion, boolean removeZipCode, boolean removeTown, boolean removeStreet )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liStartSpeller(n, bl, bl2, bl3);
    }

    public void liStopSpeller() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liStopSpeller()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liStopSpeller();
    }

    public void liStripLocation(NavLocation navLocation, int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liStripLocation( NavLocation location, int type )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liStripLocation(navLocation, n);
    }

    public void liThesaurusHistoryAdd(String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liThesaurusHistoryAdd( String wordToAdd )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liThesaurusHistoryAdd(string);
    }

    public void liThesaurusHistoryDelete(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liThesaurusHistoryDelete( int uid )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liThesaurusHistoryDelete(n);
    }

    public void liThesaurusHistoryDeleteAll() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liThesaurusHistoryDeleteAll()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liThesaurusHistoryDeleteAll();
    }

    public void liThesaurusHistoryGetEntry(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liThesaurusHistoryGetEntry( int uid )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liThesaurusHistoryGetEntry(n);
    }

    public void liTryBestMatch(TryBestMatchData tryBestMatchData) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liTryBestMatch( TryBestMatchData tbmData )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liTryBestMatch(tryBestMatchData);
    }

    public void liTryMatchLocation(TryMatchLocationData tryMatchLocationData) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liTryMatchLocation( TryMatchLocationData tmLocation )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liTryMatchLocation(tryMatchLocationData);
    }

    public void liValueListFilename(String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liValueListFilename( String liValueListFilename )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liValueListFilename(string);
    }

    public void liValueListMaximumLength(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liValueListMaximumLength( int maximumLength )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liValueListMaximumLength(n);
    }

    public void liValueListOutputMethod(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liValueListOutputMethod( int liValueListOutputMethod )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liValueListOutputMethod(n);
    }

    public void liValueListWindowSize(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("liValueListWindowSize( int windowSize )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.liValueListWindowSize(n);
    }

    public void locationToStream(NavLocation navLocation) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("locationToStream( NavLocation navLocation )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.locationToStream(navLocation);
    }

    public void poiConfigureContext(String string, int n, NavLocation navLocation, int[] nArray) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("poiConfigureContext( String initialSearchString, int poiSearchMode, NavLocation poiLocation, int[] categoryUIds )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.poiConfigureContext(string, n, navLocation, nArray);
    }

    public void poiGetCategoryTypesFromUId(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("poiGetCategoryTypesFromUId( int categoryUId )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.poiGetCategoryTypesFromUId(n);
    }

    public void poiGetXt9LDBs(NavLocation navLocation, int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("poiGetXt9LDBs( NavLocation position, int mode )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.poiGetXt9LDBs(navLocation, n);
    }

    public void poiRequestExtendedInfo(NavLocation navLocation) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("poiRequestExtendedInfo( NavLocation poi )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.poiRequestExtendedInfo(navLocation);
    }

    public void poiSelectSelectionCriteria(long l) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("poiSelectSelectionCriteria( long index )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.poiSelectSelectionCriteria(l);
    }

    public void poiSetContext(NavLocation navLocation) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("poiSetContext( NavLocation poiLocation )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.poiSetContext(navLocation);
    }

    public void poiSetListStyle(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("poiSetListStyle( int style )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.poiSetListStyle(n);
    }

    public void poiSetSortOrder2(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("poiSetSortOrder2( int poiSortOrder )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.poiSetSortOrder2(n);
    }

    public void poiStartSpellerAlongRoute(int n, long l, long l2) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("poiStartSpellerAlongRoute( int selectionCriterion, long corridor, long length )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.poiStartSpellerAlongRoute(n, l, l2);
    }

    public void poiStartSpellerAlongRouteAdvanced(int n, long l, long l2, long l3, boolean bl) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("poiStartSpellerAlongRouteAdvanced( int selectionCriterion, long corridor, long length, long offset, boolean reverse )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.poiStartSpellerAlongRouteAdvanced(n, l, l2, l3, bl);
    }

    public void requestAudioTrigger(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("requestAudioTrigger( int audioMode )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.requestAudioTrigger(n);
    }

    public void requestCountryInfo(String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("requestCountryInfo( String countryAbbreviation )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.requestCountryInfo(string);
    }

    public void requestSoPosPositionDescriptionVehicle() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("requestSoPosPositionDescriptionVehicle()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.requestSoPosPositionDescriptionVehicle();
    }

    public void rgCalculate1stRouteAndPostponeRemaining(Route route, int n, boolean bl) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgCalculate1stRouteAndPostponeRemaining( Route route, int numOfRoutes, boolean resumeRoute )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgCalculate1stRouteAndPostponeRemaining(route, n, bl);
    }

    public void rgCalculateRoute(Route route, int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgCalculateRoute( Route route, int numOfAlternatives )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgCalculateRoute(route, n);
    }

    public void rgConfigurePoiInfo(NavPoiInfoConfiguration navPoiInfoConfiguration) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgConfigurePoiInfo( NavPoiInfoConfiguration config )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgConfigurePoiInfo(navPoiInfoConfiguration);
    }

    public void rgDeleteCalculatedRubberbandPoint() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgDeleteCalculatedRubberbandPoint()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgDeleteCalculatedRubberbandPoint();
    }

    public void rgDeletePersistedRouteData() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgDeletePersistedRouteData()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgDeletePersistedRouteData();
    }

    public void rgEnableEnhancedSignPostInfo(boolean bl) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgEnableEnhancedSignPostInfo( boolean enable )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgEnableEnhancedSignPostInfo(bl);
    }

    public void rgGetLocationOnRoute(long l) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgGetLocationOnRoute( long distance )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgGetLocationOnRoute(l);
    }

    public void rgGetRouteBoundingRectangle(boolean bl, int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgGetRouteBoundingRectangle( boolean completeTour, int destinationIndex )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgGetRouteBoundingRectangle(bl, n);
    }

    public void rgGetRubberBandPointPosition() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgGetRubberBandPointPosition()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgGetRubberBandPointPosition();
    }

    public void rgPrepareRubberbandManipulation(boolean bl) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgPrepareRubberbandManipulation( boolean stopGuidance )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgPrepareRubberbandManipulation(bl);
    }

    public void rgReverseTrailDirection() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgReverseTrailDirection()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgReverseTrailDirection();
    }

    public void rgSetPosition(NavLocation navLocation) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgSetPosition( NavLocation position )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgSetPosition(navLocation);
    }

    public void rgSetRouteGuidanceMode(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgSetRouteGuidanceMode( int guidanceMode )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgSetRouteGuidanceMode(n);
    }

    public void rgSetRouteOptions(RouteOptions routeOptions) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgSetRouteOptions( RouteOptions routeOptions )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgSetRouteOptions(routeOptions);
    }

    public void rgSetRubberbandPosition(NavLocationWgs84 navLocationWgs84) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgSetRubberbandPosition( NavLocationWgs84 position )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgSetRubberbandPosition(navLocationWgs84);
    }

    public void rgSetTurnListMode(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgSetTurnListMode( int mode )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgSetTurnListMode(n);
    }

    public void rgSkipNextWayPoints(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgSkipNextWayPoints( int numberOfWaypointsToSkip )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgSkipNextWayPoints(n);
    }

    public void rgStartGuidanceCalculatedRoute(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgStartGuidanceCalculatedRoute( int routeHandle )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgStartGuidanceCalculatedRoute(n);
    }

    public void rgStartGuidanceCalculatedRouteByUID(NavSegmentID navSegmentID) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgStartGuidanceCalculatedRouteByUID( NavSegmentID uidOfCalculatedRoute )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgStartGuidanceCalculatedRouteByUID(navSegmentID);
    }

    public void rgStartRubberbandManipulation(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgStartRubberbandManipulation( int routeSectionIndex )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgStartRubberbandManipulation(n);
    }

    public void rgStopGuidance() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgStopGuidance()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgStopGuidance();
    }

    public void rgStopRouteCalculation() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgStopRouteCalculation()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgStopRouteCalculation();
    }

    public void rgStopRubberbandManipulation() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgStopRubberbandManipulation()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgStopRubberbandManipulation();
    }

    public void rgSwitchToNextPossibleRoad() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgSwitchToNextPossibleRoad()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgSwitchToNextPossibleRoad();
    }

    public void rgTriggerRCCIUpdate() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rgTriggerRCCIUpdate()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rgTriggerRCCIUpdate();
    }

    public void rmAbortImportToursFromGpxFile() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rmAbortImportToursFromGpxFile()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rmAbortImportToursFromGpxFile();
    }

    public void rmImportToursFromGpxFile(int n, String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rmImportToursFromGpxFile(int rmID, String fileName)").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rmImportToursFromGpxFile(n, string);
    }

    public void rmMakeRoutePersistent(Route route) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rmMakeRoutePersistent( Route route )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rmMakeRoutePersistent(route);
    }

    public void rmRouteAdd(int n, Route route, String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rmRouteAdd( int rmID, Route route, String name )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rmRouteAdd(n, route, string);
    }

    public void rmRouteDelete(int n, long l) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rmRouteDelete( int rmID, long routeId )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rmRouteDelete(n, l);
    }

    public void rmRouteDeleteAll(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rmRouteDeleteAll( int rmID )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rmRouteDeleteAll(n);
    }

    public void rmRouteGet(int n, long l) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rmRouteGet( int rmID, long routeId )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rmRouteGet(n, l);
    }

    public void rmRouteRename(int n, long l, String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rmRouteRename( int rmID, long routeID, String name )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rmRouteRename(n, l, string);
    }

    public void rmRouteReplace(int n, long l, Route route) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rmRouteReplace( int rmID, long routeID, Route route )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rmRouteReplace(n, l, route);
    }

    public void rrdStartCalculationByListIndex(int n, long l) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rrdStartCalculationByListIndex( int anchorIndex, long numberToCalc )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rrdStartCalculationByListIndex(n, l);
    }

    public void rrdStartCalculationForPosition(NavLocationWgs84[] navLocationWgs84Array) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rrdStartCalculationForPosition( NavLocationWgs84[] navLocations )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rrdStartCalculationForPosition(navLocationWgs84Array);
    }

    public void rrdStopCalculation() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("rrdStopCalculation()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.rrdStopCalculation();
    }

    public void setDsiNavigation(DSINavigation dSINavigation) {
        this.dsiNavigation = dSINavigation;
    }

    public void setFacadeEnabled(boolean bl) {
        if (!bl) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("setFacadeEnabled( boolean facadeEnabled )").append("' will be ignored").log();
            return;
        }
        this.facadeEnabled = bl;
    }

    public void setLanguage(String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("setLanguage( String navLanguage )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.setLanguage(string);
    }

    public void setNavInternalDataToFactorySettings() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("setNavInternalDataToFactorySettings()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.setNavInternalDataToFactorySettings();
    }

    public void setNotification(DSIListener dSIListener) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("setNotification( DSIListener listener )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.setNotification(dSIListener);
    }

    public void setNotification(int n, DSIListener dSIListener) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("setNotification( int attribute, DSIListener listener )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.setNotification(n, dSIListener);
    }

    public void setNotification(int[] nArray, DSIListener dSIListener) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("setNotification( int[] attributes, DSIListener listener )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.setNotification(nArray, dSIListener);
    }

    public void setPathsToPersonalPOIDataBases(String[] stringArray) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("setPathsToPersonalPOIDataBases( String[] paths )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.setPathsToPersonalPOIDataBases(stringArray);
    }

    public void setRemainingRangeOfVehicle(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("setRemainingRangeOfVehicle( int remainingRange )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.setRemainingRangeOfVehicle(n);
    }

    public void setTrailerStatus(boolean bl) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("setTrailerStatus( boolean trailerAttached )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.setTrailerStatus(bl);
    }

    public void setUserDefinedPOIs(NavLocation[] navLocationArray) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("setUserDefinedPOIs( NavLocation[] userDefinedPOIs )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.setUserDefinedPOIs(navLocationArray);
    }

    public void setVehicleFuelType(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("setVehicleFuelType( int vehicleFuelType )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.setVehicleFuelType(n);
    }

    public void streamToLocation(byte[] byArray) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("streamToLocation( byte[] streamLocation )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.streamToLocation(byArray);
    }

    public void translateRoute(Route route) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("translateRoute( Route navRouteList )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.translateRoute(route);
    }

    public void trCreateWaypoint() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("trCreateWaypoint()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.trCreateWaypoint();
    }

    public void trDeleteAllTraces() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("trDeleteAllTraces()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.trDeleteAllTraces();
    }

    public void trDeleteTrace(NavSegmentID navSegmentID) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("trDeleteTrace( NavSegmentID traceId )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.trDeleteTrace(navSegmentID);
    }

    public void trExportTrails(NavSegmentID[] navSegmentIDArray, String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("trExportTrails( NavSegmentID[] traceIDs, String fileName )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.trExportTrails(navSegmentIDArray, string);
    }

    public void triggerEventAudioMessage(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("triggerEventAudioMessage( int soundID )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.triggerEventAudioMessage(n);
    }

    public void trImportTrails(String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("trImportTrails( String fileName )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.trImportTrails(string);
    }

    public void trRenameTrace(NavSegmentID navSegmentID, String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("trRenameTrace( NavSegmentID traceId, String name )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.trRenameTrace(navSegmentID, string);
    }

    public void trStartTraceRecording(int n) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("trStartTraceRecording( int recordingMode )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.trStartTraceRecording(n);
    }

    public void trStopTraceRecording() {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("trStopTraceRecording()").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.trStopTraceRecording();
    }

    public void trStoreTrace(String string) {
        if (!this.facadeEnabled) {
            this.logger.makeWarn().append("The facade is disabled, the call '").append("trStoreTrace( String name )").append("' will be ignored").log();
            return;
        }
        this.dsiNavigation.trStoreTrace(string);
    }

    public void trClearRecordedTraceCache() {
    }

    public void profileChange(int n) {
    }

    public void profileCopy(int n, int n2) {
    }

    public void profileReset(int n) {
    }

    public void profileResetAll() {
    }

    public void setVirtualRouteGuidance(boolean bl) {
    }
}

