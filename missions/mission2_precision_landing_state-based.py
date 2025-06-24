import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import control.controller_functions as cl 
import utils.image_processing_raspi as ip
import utils.colors as colors
import control.logging as log
import asyncio

class MissionState:
    INIT = "INIT"
    CONNECT = "CONNECT"
    ARM = "ARM"
    SET_LOCATIONS = "SET_LOCATIONS"
    START_CAMERA = "START_CAMERA"
    TAKEOFF = "TAKEOFF"
    FLY_TO_LOCATION = "FLY_TO_LOCATION"
    SEARCH_TARGET = "SEARCH_TARGET"
    PRECISION_LAND = "PRECISION_LAND"
    LAND_AND_DISARM = "LAND_AND_DISARM"
    END = "END"

async def run(landingPosition, targetType, weatherConditions, geofence=None):
    logfile = "mission2.log"
    state = MissionState.INIT
    drone = None
    vid = None
    color = None
    home_latitude = None
    home_longitude = None
    mission_locations = None
    x_distance = None
    y_distance = None
    bool_found = False
    mission_id = 2
    land_mode = "default"

    while state != MissionState.END:
        if state == MissionState.INIT:
            log.log("---------------------------------", logfile)
            log.log("Mission 2 gestartet", logfile)
            log.log(f"Mission 2 gestartet mit Landeposition: {landingPosition}, Zieltyp: {targetType}, Wetterbedingungen: {weatherConditions}", logfile)
            if geofence:
                log.log(f"Geofence aktiviert mit Punkten: {geofence}", logfile)
            else:
                log.log("Geofence über QGC gesetzt", logfile)
            state = MissionState.CONNECT

        elif state == MissionState.CONNECT:
            log.log("🔌 Connecting to drone...", logfile)
            drone = await cl.connect_drone(logfile)
            log.log("✅ Drone connected.", logfile)
            state = MissionState.ARM

        elif state == MissionState.ARM:
            log.log("🔒 Arming drone...", logfile)
            await cl.arm_drone(drone, logfile)
            log.log("✅ Drone armed.", logfile)
            state = MissionState.SET_LOCATIONS

        elif state == MissionState.SET_LOCATIONS:
            log.log("📍 Fetching home location...", logfile)
            home = await drone.telemetry.home().__anext__()
            home_latitude = home.latitude_deg
            home_longitude = home.longitude_deg
            mission_locations = landingPosition  # target location
            log.log(f"📍 Home location set to: {(home_latitude, home_longitude)}", logfile)
            log.log(f"🗺️ Target location: {mission_locations}", logfile)
            state = MissionState.START_CAMERA

        elif state == MissionState.START_CAMERA:
            log.log("📷 Starting video capture...", logfile)
            color = colors.map_color_to_id(targetType)
            vid = ip.start_videoCapture(mission_id, weatherConditions, logfile)
            log.log(f"✅ Video capture started. Target color: {color}", logfile)
            state = MissionState.TAKEOFF

        elif state == MissionState.TAKEOFF:
            target_altitude = 5.0
            log.log(f"🚁 Taking off to {target_altitude} meters...", logfile)
            await cl.default_takeoff(drone, target_altitude, logfile)
            await asyncio.sleep(1)
            log.log("✅ Takeoff complete.", logfile)
            state = MissionState.FLY_TO_LOCATION

        elif state == MissionState.FLY_TO_LOCATION:
            target_altitude = 15.0
            latitude, longitude = mission_locations[0]
            log.log(
                f"🟣 Flying to single location: "
                f"{latitude}, {longitude}, {target_altitude} m", logfile
            )
            await cl.goto_location(drone, latitude, longitude, target_altitude, logfile)
            await drone.action.hold()
            log.log("🛑 Holding at target location.", logfile)
            state = MissionState.SEARCH_TARGET

        elif state == MissionState.SEARCH_TARGET:
            position = await drone.telemetry.position().__anext__()
            center_lat = position.latitude_deg
            center_lon = position.longitude_deg
            log.log("🔍 Searching for target...", logfile)
            for _ in range(4):
                x_distance, y_distance = await ip.main_mission_2(drone, vid, color, weatherConditions, logfile)
            if x_distance is None or y_distance is None:
                log.log("❌ TARGET NOT FOUND. Initiating spiral search.", logfile)
                bool_found = await cl.fly_spiral_search(
                    drone, center_lat, center_lon, vid, color, weatherConditions, 15.0, logfile
                )
            else:
                log.log("✅ Target detected.", logfile)
                bool_found = True
            state = MissionState.PRECISION_LAND if bool_found else MissionState.LAND_AND_DISARM

        elif state == MissionState.PRECISION_LAND:
            log.log("🟢 Initiating precision landing...", logfile)
            await cl.precision_land_velocity_pid_method(drone, vid, color, weatherConditions, land_mode, logfile)
            ip.stop_videoCapture(vid, logfile)
            log.log("✅ Precision landing complete. Video stopped.", logfile)
            state = MissionState.END

        elif state == MissionState.LAND_AND_DISARM:
            log.log("🛬 No target found, returning to home location.", logfile)
            await cl.goto_location(drone, home_latitude, home_longitude, 15.0, logfile)
            await cl.default_land_and_disarm(drone, logfile)
            ip.stop_videoCapture(vid, logfile)
            log.log("✅ Landed at home. Video stopped.", logfile)
            state = MissionState.END

        else:
            log.log("⚠️ Unknown state, ending mission.", logfile)
            state = MissionState.END