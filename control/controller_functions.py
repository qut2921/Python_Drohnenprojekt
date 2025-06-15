"""
Comands to controle the mission with repeating modules

"""
import json
import control.logging as log
import control.error_message as em
import math
from mavsdk.telemetry import LandedState
import utils.image_processing_raspi as ip
from mavsdk.offboard import PositionNedYaw
from mavsdk.offboard import VelocityNedYaw
from mavsdk import System
import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


STATE_FILE = "mission1_state.json"


async def connect_drone(logfile) -> System:
    """
    Connects to the drone via MAVSDK.

    Returns:
        System: The connected MAVSDK drone object.
    """
    drone = System()
    print("----------------------")
    log.log("🔄 Connecting to drone...", logfile)
    try:
        # Connect to the drone to SITL
        # await drone.connect(system_address="udp://:14540")
        # Connect to the drone to real hardware
        await drone.connect(system_address="serial:///dev/ttyAMA0:57600")
    except Exception as e:
        log.log(f"❌ Error connecting to drone: {e}", logfile)
        return
    await asyncio.sleep(1)
    log.log("✅ Drone connected\n", logfile)
    return drone


async def arm_drone(drone, logfile):
    """
    Arms the drone.

    Inputs:
        drone (System): MAVSDK drone object to send commands.

    Steps:
        - Waits for connection to the drone
        - Arms the drone
    """
    log.log("🔄 Arming...", logfile)
    try:
        await drone.action.arm()
        log.log("✅ Drone armed\n", logfile)
    except Exception as e:
        message = f"❌ Error arming drone: {e}"
        log.log(message, logfile)
        return


async def default_takeoff(drone, target_altitude, logfile):
    """
    Arms the drone and performs an automatic takeoff.

    Inputs:
        drone (System): MAVSDK drone object to send commands.
        target_altitude (float, optional): Target altitude in meters.
        Default is 10.0 m.

    Steps:
        - Waits for connection to the drone
        - Arms the drone
        - Sets the target takeoff altitude
        - Initiates takeoff
        - Waits until target altitude (±0.5m) is reached
    """

    # await drone.param.set_param_float("MPC_TKO_SPEED", 2.0) # 2 m/s
    await drone.action.set_takeoff_altitude(target_altitude)

    log.log(f"🟣 Taking off to {target_altitude} m", logfile)
    try:
        await drone.action.takeoff()
    except Exception as e:
        message = f"❌ Error taking off: {e}"
        log.log(message, logfile)
        return
    log.log("🔄 Taking off...", logfile)
    # Waits until the drone reaches the target altitude
    while True:
        position = await drone.telemetry.position().__anext__()
        current_alt = position.relative_altitude_m
        print(f"\r⬆️ Current height: {current_alt:.1f} m", end="")
        
        # Optional: akzeptiere mehr Toleranz bei Wiederstart
        if abs(current_alt - target_altitude) < 0.2:
            print("\n✅ Target altitude reached")
            break


async def check_battery(drone: System):
    """
    Checks the battery level of the drone.

    Inputs:
        drone (System): MAVSDK drone object to send commands.

    Steps:
        - Retrieves the battery level
        - Prints the battery level
    """
    print("Checking battery level...")
    # Gives the battery level in percent
    async for battery in drone.telemetry.battery():
        print(f"Battery: {battery.remaining_percent * 100:.1f}%")
        await asyncio.sleep(0.2)
        if battery.remaining_percent < 0.2:
            print("Battery low, returning to launch")
            await drone.action.return_to_launch()
            break


async def fail_safe(drone: System):
    """
    Initiates fail-safe procedures for the drone.

    Inputs:
        drone (System): MAVSDK drone object to send commands.

    Checks:
        - Checks the battery level
        - Checks the GPS status
    """
    print("Fail-safe initiated")
    await check_battery(drone)
    print("Fail-safe completed")
    # Checks the battery level of the drone
    battery = await drone.telemetry.battery()
    if battery.remaining_percent < 0.2:
        print("Battery low, returning to launch")
        await drone.action.return_to_launch()

    # Checks the drone's GPS status
    gps_info = await drone.telemetry.gps_info()
    if gps_info.num_satellites_visible < 5:
        print("GPS signal weak, returning to launch")
        await drone.action.return_to_launch()


async def goto_location(drone: System, target_latitude: float,
                        target_longitude: float,
                        target_altitude: float, logfile):
    """
    Commands the drone to fly to a specific GPS location.

    Inputs:
        drone (System): MAVSDK drone object to send commands.
        target_latitude (float): Target latitude in degrees.
        target_longitude (float): Target longitude in degrees.
        target_altitude (float): Target altitude in meters.

    Steps:
        - Sets the drone's mode to "GUIDED"
        - Commands the drone to fly to the specified GPS location
    """
    # Sets home location
    home = await drone.telemetry.home().__anext__()
    home_abs_alt = home.absolute_altitude_m
    # Transforms the target altitude to absolute altitude + target altitude
    target_absolute_alt = home_abs_alt + target_altitude
    # Flys to the target location
    await drone.action.goto_location(target_latitude,
                                     target_longitude,
                                     target_absolute_alt,
                                     0.0)
    log.log("🔄 Flying to target location...", logfile)
    # Waits until the drone reaches the target location
    while True:
        position = await drone.telemetry.position().__anext__()
        current_latitude = position.latitude_deg
        current_longitude = position.longitude_deg
        current_height = position.relative_altitude_m

        print(
            f"\r➡️ Current location: {current_latitude:.7f}, "
            f"{current_longitude:.7f}, {current_height:.1f} m",
            end=""
        )

        # Checks if the drone reached target
        if (abs(current_latitude - target_latitude) < 0.000005 and
                abs(current_longitude - target_longitude) < 0.00005 and
                abs(current_height - target_altitude) < 0.1):
            log.log("\n✅ Target location reached\n", logfile)
            break


async def default_land_and_disarm(drone: System, logfile):
    """
    Commands the drone to land.

    Inputs:
        drone (System): MAVSDK drone object to send commands.

    Steps:
        - Sets the drone's mode to "LAND"
        - Initiates landing
    """
    try:
        await drone.action.land()
    except Exception as e:
        message = f"❌ Error landing: {e}"
        log.log(message, logfile)
        return

    log.log("🔄 Landing...", logfile)
    async for state in drone.telemetry.landed_state():
        print(f"\r🔍 Landed State: {state}", end="")
        if state == LandedState.ON_GROUND:
            log.log("\n✅ Drone is confirmed landed.\n", logfile)
            break

    log.log("🔄 Disarming...", logfile)
    try:
        await drone.action.disarm()
        log.log("✅ Drone disarmed\n", logfile)
    except Exception as e:
        message = f"❌ Failed to disarm: {e}"
        log.log(message, logfile)
        return

    log.log("✅ Mission completed ✅", logfile)
    print("----------------------")


def pid_update(error, dt, state, kp, ki, kd, max_output=1.0):
    state["integral"] += error * dt
    derivative = (error - state["prev_error"]) / dt
    output = kp * error + ki * state["integral"] + kd * derivative
    state["prev_error"] = error
    return max(-max_output, min(max_output, output)), state


async def precision_land_velocity_pid_method(drone, vid, color, mission_id, logfile):
    """
    Precision Landing via velocity control using PID implemented as function.
    Landing occurs when height < 0.5 m.
    """

    pid_params = {"kp": 0.8, "ki": 0.05, "kd": 0.1}  # PID parameters
    max_speed = 1.0  # m/s – max speed
    descent_speed = 0.5  # m/s
    landing_threshold = 2  # m
    alignment_threshold = 0.1  # m threshold for alignment
    alignment_stable_time = 2.0  # seconds to consider alignment stable
    dt = 0.1  # time step in seconds

    # Initialize PID states
    state_north = {"integral": 0.0, "prev_error": 0.0}
    state_east = {"integral": 0.0, "prev_error": 0.0}
    stable_time = 0.0

    # 0. Start Offboard mode
    await drone.offboard.set_velocity_ned(VelocityNedYaw(0, 0, 0, 0))
    await asyncio.sleep(0.1)

    try:
        await drone.offboard.start()
        log.log("🟢 Offboard mode started", logfile)
    except Exception as e:
        log.log(f"❌ Failed to start offboard: {e}", logfile)
        return

    # 1. Horizontal alignment phase
    while True:
        delta_north, delta_east = await ip.main_mission_2(drone, vid, color)

        if delta_north is None or delta_east is None:
            log.log("⚠️ No target detected. Stopping movement...", logfile)
            await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
            stable_time = 0.0
            await asyncio.sleep(dt)
            continue

        v_north, state_north = pid_update(delta_north, dt, state_north, **pid_params, max_output=max_speed)
        v_east,  state_east  = pid_update(delta_east,  dt, state_east,  **pid_params, max_output=max_speed)

        await drone.offboard.set_velocity_ned(VelocityNedYaw(
            north_m_s=v_north,
            east_m_s=v_east,
            down_m_s=0.0,
            yaw_deg=0.0
        ))

        print(f"\r🟡 Aligning: vN={v_north:.2f}, vE={v_east:.2f} – ΔN={delta_north:.2f}, ΔE={delta_east:.2f}", end="")

        if abs(delta_north) < alignment_threshold and abs(delta_east) < alignment_threshold:
            stable_time += dt
            if stable_time >= alignment_stable_time:
                log.log("✅ Alignment complete. Starting descent.\n", logfile)
                break
        else:
            stable_time = 0.0

        await asyncio.sleep(dt)

    # 2. Precision Landing phase with descent
    while True:
        delta_north, delta_east = await ip.main_mission_2(drone, vid, color)

        if delta_north is None or delta_east is None:
            log.log("⚠️ No target detected. Stopping movement...", logfile)
            await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
            await asyncio.sleep(dt)
            continue

        v_north, state_north = pid_update(delta_north, dt, state_north, **pid_params, max_output=max_speed)
        v_east,  state_east  = pid_update(delta_east,  dt, state_east,  **pid_params, max_output=max_speed)

        await drone.offboard.set_velocity_ned(VelocityNedYaw(
            north_m_s=v_north,
            east_m_s=v_east,
            down_m_s=descent_speed,
            yaw_deg=0.0
        ))

        position = await drone.telemetry.position().__anext__()
        current_alt = position.relative_altitude_m
        print(f"\r✈️ vN={v_north:.2f}, vE={v_east:.2f}, Alt={current_alt:.2f} m", end="")

        if current_alt < landing_threshold:
            log.log("\n✅ Altitude < 0.5 m → Landing\n", logfile)

            if mission_id == 2:
                await default_land_and_disarm(drone, logfile)
            elif mission_id == 3:
                try:
                    await drone.param.set_param_float("COM_DISARM_LAND", 0.0)
                    log.log("🔧 Set COM_DISARM_LAND = 0.0 to prevent auto-disarm", logfile)
                except Exception as e:
                    log.log(f"⚠️ Could not set COM_DISARM_LAND: {e}", logfile)
                await drone.action.land()

            break

        await asyncio.sleep(dt)


async def precision_land_test(drone, mission_id, n_ned, e_ned, logfile):
    """
    Precision Landing via velocity control using PID implemented as function.
    Landing occurs when height < 0.5 m.
    """

    pid_params = {"kp": 0.8, "ki": 0.05, "kd": 0.1}  # PID parameters
    max_speed = 1.0  # m/s – max speed
    descent_speed = 0.5  # m/s
    landing_threshold = 2  # m
    alignment_threshold = 0.1  # m threshold for alignment
    alignment_stable_time = 2.0  # seconds to consider alignment stable
    dt = 0.1  # time step in seconds

    # Initialize PID states for north and east directions
    state_north = {"integral": 0.0, "prev_error": 0.0}
    state_east = {"integral": 0.0, "prev_error": 0.0}

    # 0. Start Offboard mode
    await drone.offboard.set_velocity_ned(VelocityNedYaw(0, 0, 0, 0))
    await asyncio.sleep(0.1)

    try:
        await drone.offboard.start()
        log.log("🟢 Offboard mode started", logfile)
    except Exception as e:
        log.log(f"❌ Failed to start offboard: {e}", logfile)
        return

    # Aktueller Offset
    delta_north = n_ned
    delta_east = e_ned

    # 1. Horizontal alignment phase
    while True:
        v_north, state_north = pid_update(
            delta_north, dt, state_north, **pid_params, max_output=max_speed)
        v_east,  state_east = pid_update(
            delta_east, dt, state_east, **pid_params, max_output=max_speed)

        # Drohne fliegt und korrigiert Position
        await drone.offboard.set_velocity_ned(VelocityNedYaw(
            north_m_s=v_north,
            east_m_s=v_east,
            down_m_s=0.0,
            yaw_deg=0.0
        ))

        print(f"\r🟡 Aligning: vN={v_north:.2f}, vE={v_east:.2f} – ΔN={delta_north:.2f}, ΔE={delta_east:.2f}", end="")

        # Simulierter Effekt der Korrektur auf den Offset
        delta_north -= v_north * dt
        delta_east -= v_east * dt

        if abs(delta_north) < alignment_threshold and abs(delta_east) < alignment_threshold:
            stable_time += dt
            if stable_time >= alignment_stable_time:
                await drone.offboard.set_velocity_ned(VelocityNedYaw(0, 0, 0, 0))
                log.log("✅ Alignment complete. Starting descent.\n", logfile)
                break
        else:
            stable_time = 0.0

        await asyncio.sleep(dt)

    # 2. Precision Landing phase with descent
    while True:
        v_north, state_north = pid_update(
            delta_north, dt, state_north, **pid_params, max_output=max_speed)
        v_east,  state_east = pid_update(
            delta_east, dt, state_east, **pid_params, max_output=max_speed)

        await drone.offboard.set_velocity_ned(VelocityNedYaw(
            north_m_s=v_north,
            east_m_s=v_east,
            down_m_s=descent_speed,
            yaw_deg=0.0
        ))

        position = await drone.telemetry.position().__anext__()
        current_alt = position.relative_altitude_m
        print(f"\r✈️ vN={v_north:.2f}, vE={v_east:.2f}, Alt={current_alt:.2f} m", end="")

        delta_north -= v_north * dt
        delta_east -= v_east * dt

        if current_alt < landing_threshold:
            log.log("\n✅ Altitude < 0.5 m → Landing\n", logfile)

            if mission_id == 2:
                await default_land_and_disarm(drone, logfile)
            elif mission_id == 3:
                # prevent auto-disarm by setting COM_DISARM_LAND = 0
                try:
                    await drone.param.set_param_float("COM_DISARM_LAND", 0.0)
                    log.log("🔧 Set COM_DISARM_LAND = 0.0 to prevent auto-disarm", logfile)
                except Exception as e:
                    log.log(f"⚠️ Could not set COM_DISARM_LAND: {e}", logfile)
                await drone.action.land()

            break

        await asyncio.sleep(dt)


async def indoor_alignment_test(drone, vid, color, logfile):
    """
    Indoor Precision Alignment Test – nur horizontale Ausrichtung ohne Sinkflug.
    Positionsfehler (delta_north, delta_east) wird aus dem Tracking- oder Bildsystem über ip.main_mission_2 bezogen.
    """

    pid_params = {"kp": 0.8, "ki": 0.05, "kd": 0.1}
    max_speed = 0.5  # m/s
    alignment_threshold = 0.1  # m
    alignment_stable_time = 2.0  # s
    dt = 0.1  # s

    state_north = {"integral": 0.0, "prev_error": 0.0}
    state_east = {"integral": 0.0, "prev_error": 0.0}
    stable_time = 0.0

    await drone.offboard.set_velocity_ned(VelocityNedYaw(0, 0, 0, 0))
    await asyncio.sleep(0.1)

    try:
        await drone.offboard.start()
        log.log("🟢 Offboard mode started", logfile)
    except Exception as e:
        log.log(f"❌ Failed to start offboard: {e}", logfile)
        return

    while True:
        delta_north, delta_east = await ip.main_mission_2(drone, vid, color)

        if delta_north is None or delta_east is None:
            log.log("⚠️ Kein Ziel erkannt. Hover...", logfile)
            await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
            await asyncio.sleep(dt)
            continue

        v_north, state_north = pid_update(
            delta_north, dt, state_north, **pid_params, max_output=max_speed)
        v_east, state_east = pid_update(
            delta_east, dt, state_east, **pid_params, max_output=max_speed)

        await drone.offboard.set_velocity_ned(VelocityNedYaw(
            north_m_s=v_north,
            east_m_s=v_east,
            down_m_s=0.0,
            yaw_deg=0.0
        ))

        print(f"\r🟡 Aligning: vN={v_north:.2f}, vE={v_east:.2f} – ΔN={delta_north:.2f}, ΔE={delta_east:.2f}", end="")

        if abs(delta_north) < alignment_threshold and abs(delta_east) < alignment_threshold:
            stable_time += dt
            if stable_time >= alignment_stable_time:
                await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
                log.log("✅ Alignment erfolgreich (Indoor-Test)", logfile)
                break
        else:
            stable_time = 0.0

        await asyncio.sleep(dt)


def offset_coordinates(lat: float, lon: float,
                       north_m: float, east_m: float) -> tuple:
    """
    calculates new GPS coordinates based on north/east offset (in meters).
    """
    earth_radius = 6378137.0
    d_lat = north_m / earth_radius
    d_lon = east_m / (earth_radius * math.cos(math.pi * lat / 180.0))
    return lat + (d_lat * 180.0 / math.pi), lon + (d_lon * 180.0 / math.pi)


async def fly_spiral_search(
    drone,
    center_lat,
    center_lon,
    vid,
    color,
    target_altitude,
    logfile
) -> bool:
    """
    Performs a tight spiral search around a GPS center point
    Stops if the camera detects a target.

    :return: True if a target is detected, otherwise False
    """
    max_radius = 10.0
    radius_step = 5
    points_per_circle = 4
    radius = radius_step
    angle = 0.0

    while radius <= max_radius:
        angle_step = 2 * math.pi / points_per_circle

        for _ in range(points_per_circle):
            # Berechne Versatz in Metern
            offset_north = radius * math.cos(angle)
            offset_east = radius * math.sin(angle)

            # Konvertiere zu GPS
            wp_lat, wp_lon = offset_coordinates(
                center_lat, center_lon, offset_north, offset_east)

            await goto_location(drone, wp_lat, wp_lon, target_altitude, logfile)
            await asyncio.sleep(2)  # Wartezeit für Kamera

            # Chechk if the camera detects a target
            n_ned, e_ned = await ip.main_mission_2(drone, vid, color)
            if n_ned is not None and e_ned is not None:
                return True  # Target found, exit the spiral search

            angle += angle_step

        radius += radius_step

    log.log("❌ no target found in the tight spiral.", logfile)
    return False


def save_progress(index):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_index": index}, f)


def load_progress():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_index", 0)
    return 0


def reset_progress():
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
