import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import control.controller_functions as cl
import utils.image_processing_raspi as ip
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

async def run(landingPosition, waypoints, weatherConditions, geofence=None):
    """
    Mission 1 (State-based)
    """
    logfile = "mission1.log"
    state = MissionState.INIT
    drone = None
    vid = None
    sequence = 0
    home_lat = None
    home_long = None
    mission_locations = []
    target_altitude = 5.0

    while state != MissionState.END:
        if state == MissionState.INIT:
            log.log("---------------------------------", logfile)
            log.log("Mission 1 gestartet", logfile)
            log.log(f"Mission 1 gestartet mit Landeposition: {landingPosition}, Wegpunkte: {waypoints}, Wetterbedingungen: {weatherConditions}", logfile)
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
            home_lat = home.latitude_deg
            home_long = home.longitude_deg
            landingPosition = (home_lat, home_long)
            mission_locations = waypoints + [landingPosition]
            log.log(f"📍 Home location set to: {landingPosition}", logfile)
            log.log(f"🗺️ Mission locations: {mission_locations}", logfile)
            state = MissionState.START_CAMERA

        elif state == MissionState.START_CAMERA:
            log.log("📷 Starting video capture...", logfile)
            vid = ip.start_videoCapture(1, weatherConditions, logfile)
            sequence = 0
            log.log("✅ Video capture started.", logfile)
            state = MissionState.TAKEOFF

        elif state == MissionState.TAKEOFF:
            target_altitude = 5.0
            log.log(f"🚁 Taking off to {target_altitude} meters...", logfile)
            await cl.default_takeoff(drone, target_altitude, logfile)
            await asyncio.sleep(1)
            log.log("✅ Takeoff complete.", logfile)
            state = MissionState.FLY_TO_LOCATIONS

        elif state == MissionState.FLY_TO_LOCATIONS:
            start_index = cl.load_progress()
            target_altitude = 15.0
            log.log(f"🛫 Starting waypoint navigation at {target_altitude} meters.", logfile)
            for i, (latitude, longitude) in enumerate(mission_locations, start=1):
                if i <= start_index:
                    log.log(f"\n⏭️ Skipping location {i} (already completed)", logfile)
                    continue
                log.log(
                    f"\n🟣 Flying to location {i}/{len(mission_locations)}: "
                    f"{latitude}, {longitude}, {target_altitude} m", logfile
                )
                await cl.goto_location(drone, latitude, longitude, target_altitude, logfile)
                await drone.action.hold()
                log.log(f"🛑 Holding at location {i}.", logfile)
                if i < len(mission_locations):
                    log.log(f"⏳ Executing mission action at location {i}.", logfile)
                    sequence = await ip.main_mission_1(drone, vid, sequence, logfile)
                    cl.save_progress(i)
                    log.log(f"💾 Progress saved at location {i}.", logfile)
                else:
                    log.log("🏁 Final point reached – skipping wait, preparing to land.", logfile)
            state = MissionState.LAND_AND_DISARM

        elif state == MissionState.LAND_AND_DISARM:
            log.log("🛬 Landing and disarming...", logfile)
            await cl.default_land_and_disarm(drone, logfile)
            ip.stop_videoCapture(vid, logfile)
            cl.reset_progress()
            log.log("✅ Mission complete. Progress reset and video stopped.", logfile)
            state = MissionState.END

        else:
            log.log("⚠️ Unknown state, ending mission.", logfile)
            state = MissionState.END