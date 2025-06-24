import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import control.controller_functions as cl 
import utils.image_processing_raspi as ip
import utils.colors as colors
from mavsdk.telemetry import LandedState
import control.logging as log
import asyncio

class MissionState:
    INIT = "INIT"
    CONNECT = "CONNECT"
    ARM = "ARM"
    SET_LOCATIONS = "SET_LOCATIONS"
    START_CAMERA = "START_CAMERA"
    TAKEOFF = "TAKEOFF"
    FLY_TO_LOCATIONS = "FLY_TO_LOCATIONS"
    LAND_AND_DISARM = "LAND_AND_DISARM"
    END = "END"

async def run(landingPosition, waypoints, targetNumber, targetType, weatherConditions, geofence=None):
    logfile = "mission3.log"
    state = MissionState.INIT
    drone = None
    vid = None
    color = None
    home_lat = None
    home_long = None
    mission_locations = []
    target_altitude = 15.0
    mission_id = 3
    land_mode = "default"

    while state != MissionState.END:
        if state == MissionState.INIT:
            log.log("---------------------------------", logfile)
            log.log("Mission 3 gestartet", logfile)
            log.log(f"Mission 3 gestartet mit Landeposition: {landingPosition}, Wegpunkte: {waypoints}, Zielanzahl: {targetNumber}, Wetterbedingungen: {weatherConditions}", logfile)
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
            await asyncio.sleep(1)
            try:
                await drone.param.set_param_float("COM_DISARM_LAND", 0.0)
                log.log("🔧 Set COM_DISARM_LAND = 0.0 to prevent auto-disarm", logfile)
            except Exception as e:
                log.log(f"⚠️ Could not set COM_DISARM_LAND: {e}", logfile)
            log.log("✅ Drone armed.", logfile)
            state = MissionState.SET_LOCATIONS

        elif state == MissionState.SET_LOCATIONS:
            log.log("📍 Fetching home location...", logfile)
            home = await drone.telemetry.home().__anext__()
            home_lat = home.latitude_deg
            home_long = home.longitude_deg
            landingPosition = (home_lat, home_long)
            mission_locations = waypoints + [landingPosition]
            log.log(f"📍 Home location set to: {landingPosition}", logfile)
            log.log(f"🗺️ Mission locations: {mission_locations}", logfile)
            state = MissionState.START_CAMERA

        elif state == MissionState.START_CAMERA:
            log.log("📷 Starting video capture...", logfile)
            color = colors.map_color_to_id(targetType)
            vid = ip.start_videoCapture(mission_id, weatherConditions, logfile)
            log.log(f"✅ Video capture started. Target color: {color}", logfile)
            state = MissionState.TAKEOFF

        elif state == MissionState.TAKEOFF:
            log.log(f"🚁 Taking off to {target_altitude} meters...", logfile)
            await cl.default_takeoff(drone, target_altitude, logfile)
            await asyncio.sleep(1)
            log.log("✅ Takeoff complete.", logfile)
            state = MissionState.FLY_TO_LOCATIONS

        elif state == MissionState.FLY_TO_LOCATIONS:
            start_index = cl.load_progress()
            log.log(f"🛫 Starting waypoint navigation at {target_altitude} meters.", logfile)
            for i, (latitude, longitude) in enumerate(mission_locations, start=1):
                if i <= start_index:
                    log.log(f"⏭️ Skipping location {i} (already completed)", logfile)
                    continue
                log.log(
                    f"\n🟣 Flying to location {i}/{len(mission_locations)}: "
                    f"{latitude}, {longitude}, {target_altitude} m, Color: {color}", logfile
                )
                await cl.goto_location(drone, latitude, longitude, target_altitude, logfile)
                await drone.action.hold()
                log.log(f"🛑 Holding at location {i}.", logfile)
                if i < len(mission_locations):
                    position = await drone.telemetry.position().__anext__()
                    center_lat = position.latitude_deg
                    center_lon = position.longitude_deg
                    log.log(f"🔍 Searching for target at location {i}...", logfile)
                    for _ in range(4):
                        x_distance, y_distance = await ip.main_mission_2(drone, vid, color, weatherConditions, logfile)
                    if x_distance is None or y_distance is None:
                        log.log("❌ TARGET NOT FOUND. Initiating spiral search.", logfile)
                        bool_found = await cl.fly_spiral_search(
                            drone, center_lat, center_lon, vid, color, weatherConditions, target_altitude, logfile
                        )
                    else:
                        log.log("✅ Target detected.", logfile)
                        bool_found = True
                    if not bool_found:
                        log.log("➡️ Target not found after spiral search, moving to next location.", logfile)
                        continue
                    else:
                        log.log("🟢 Initiating precision landing...", logfile)
                        await cl.precision_land_velocity_pid_method(drone, vid, color, weatherConditions, land_mode, logfile)
                    async for state_landed in drone.telemetry.landed_state():
                        print(f"\r🔍 Landed State: {state_landed}", end="")
                        if state_landed == LandedState.ON_GROUND:
                            log.log("✅ Drone is confirmed landed.", logfile)
                            log.log("Takeoff again in 5s", logfile)
                            await asyncio.sleep(5)
                            await cl.default_takeoff(drone, target_altitude, logfile)
                            break
                else:
                    log.log("✅ All locations completed.", logfile)
                    break
            state = MissionState.LAND_AND_DISARM

        elif state == MissionState.LAND_AND_DISARM:
            log.log("🛬 Landing and disarming...", logfile)
            await cl.default_land_and_disarm(drone, logfile)
            ip.stop_videoCapture(vid, logfile)
            log.log("✅ Mission complete. Progress reset and video stopped.", logfile)
            state = MissionState.END

        else:
            log.log("⚠️ Unknown state, ending mission.", logfile)
            state = MissionState.END