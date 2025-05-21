"""
Comands to controle the mission with repeating modules

"""

print(__file__)

import asyncio
from mavsdk import System
from mavsdk.offboard import VelocityNedYaw
from mavsdk.offboard import PositionNedYaw
import math
import modules.error_message as em


async def connect_drone() -> System:
    """
    Connects to the drone via MAVSDK.

    Returns:
        System: The connected MAVSDK drone object.
    """
    drone = System()
    print("----------------------")
    print("🔄 Connecting to drone...")
    try:
        # Connect to the drone to SITL
        #await drone.connect(system_address="udp://:14540")
        # Connect to the drone to real hardware
        await drone.connect(system_address="serial:///dev/ttyAMA0:57600")
    except Exception as e:
        print(f"❌ Error connecting to drone: {e}")
        return
    print("✅ Drone connected")
    await asyncio.sleep(0.5)
    return drone


async def arm_drone(drone: System):
    """
    Arms the drone.

    Inputs:
        drone (System): MAVSDK drone object to send commands.

    Steps:
        - Waits for connection to the drone
        - Arms the drone
    """
    print("\n🔄 Arming...")
    try:
        await drone.action.arm()
    except Exception as e:
        message = f"❌ Error arming drone: {e}"
        print(message)
        em.log(message)
        return
    print("✅ Drone armed")


async def default_takeoff(drone: System, target_altitude: float = 10.0):
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

    await drone.param.set_param_float("MPC_TKO_SPEED", 2.0) # 2 m/s
    await drone.action.set_takeoff_altitude(target_altitude)

    print("Start Mission")

    print(f"\n🟣 Taking off to {target_altitude} m")
    try:
        await drone.action.takeoff()
    except Exception as e:
        message = f"❌ Error taking off: {e}"
        print(message)
        em.log(message)
        return
    print("🔄 Taking off...")
    # Waits until the drone reaches the target altitude
    async for position in drone.telemetry.position():
        current_height = position.relative_altitude_m
        print(f"\r⬆️ Current height: {current_height:.1f} m", end="")
        if abs(current_height - target_altitude) < 0.1:
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
                        target_altitude: float):
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
    print("🔄 Flying to target location...")
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
            print("\n✅ Target location reached")
            break
        await asyncio.sleep(0.2)


async def default_land_and_disarm(drone: System):
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
        print(message)
        em.log(message)
        return
    print("\n🔄 Landing...")
    async for position in drone.telemetry.position():
        current_height = position.relative_altitude_m
        print(f"\r⬇️ Current height: {current_height:.1f} m", end="")
        if abs(current_height) < 0.1:
            print("\n✅ Landed")
            break
    
    # Disarm the drone after landing
    await asyncio.sleep(2)
    print("\n🔄 Disarming...")
    try:
        await drone.action.disarm()
        print("✅ Drone disarmed")
    except Exception as e:
        message = f"❌ Failed to disarm: {e}"
        print(message)
        em.log(message)
        message = "✅ Mission completed ✅"
        print(message)
        em.log(message)
        message = "----------------------"
        print(message)
        em.log(message)

    print("✅ Mission completed ✅")
    print("----------------------")


def pid_update(error, dt, state, kp, ki, kd, max_output=1.0):
    state["integral"] += error * dt
    derivative = (error - state["prev_error"]) / dt
    output = kp * error + ki * state["integral"] + kd * derivative
    state["prev_error"] = error
    return max(-max_output, min(max_output, output)), state

async def precision_land_velocity_pid_method(drone, image_processing):
    """
    Precision Landing via velocity control using PID implemented as function.
    Landing occurs when height < 0.5 m, regardless of position error.
    """

    # Reglerparameter
    pid_params = {"kp": 0.8, "ki": 0.1, "kd": 0.08}
    max_speed = 1.0
    descent_speed = 0.3  # m/s
    landing_threshold = 0.5  # m
    dt = 0.1  # 100 ms

    # PID-Zustände
    state_north = {"integral": 0.0, "prev_error": 0.0}
    state_east  = {"integral": 0.0, "prev_error": 0.0}

    # Dummy-Setpoint zum Aktivieren von Offboard
    await drone.offboard.set_velocity_ned(VelocityNedYaw(0, 0, 0, 0))
    await asyncio.sleep(0.1)

    try:
        await drone.offboard.start()
        print("🟢 Offboard mode started")
    except Exception as e:
        message = f"❌ Failed to start offboard: {e}"
        print(message)
        em.log(message)
        return

    while True:
        # 1. Bildverarbeitung liefert Abweichung in m
        delta_north, delta_east = image_processing.get_target_offset()

        # 2. PID-Regelung
        v_north, state_north = pid_update(delta_north, dt, state_north, **pid_params, max_output=max_speed)
        v_east,  state_east  = pid_update(delta_east, dt, state_east, **pid_params, max_output=max_speed)
        v_down = descent_speed

        # 3. Steuerbefehl senden
        await drone.offboard.set_velocity_ned(VelocityNedYaw(
            north_m_s=-v_north,  # negative Richtung → Annäherung
            east_m_s=-v_east,
            down_m_s=v_down,
            yaw_deg=0.0
        ))

        # 4. Höhe prüfen
        position = await drone.telemetry.position().__anext__()
        current_alt = position.relative_altitude_m
        print(f"\r✈️ vN: {v_north:.2f}, vE: {v_east:.2f}, Alt: {current_alt:.2f} m", end="")

        if current_alt < landing_threshold:
            print("\n✅ Altitude < 0.5 m → Landing")
            await drone.action.land()
            break

        await asyncio.sleep(dt)



def offset_coordinates(lat: float, lon: float, 
                       north_m: float, east_m: float)-> tuple:
    """
    calculates new GPS coordinates based on north/east offset (in meters).
    """
    earth_radius = 6378137.0
    d_lat = north_m / earth_radius
    d_lon = east_m / (earth_radius * math.cos(math.pi * lat / 180.0))
    return lat + (d_lat * 180.0 / math.pi), lon + (d_lon * 180.0 / math.pi)


async def fly_spiral_search(
    drone: System,
    center_lat = 48.7647846,
    center_lon = 16.5487951,
    target_altitude = 15.0,
    max_radius = 2.5,
    radius_step = 0.5,
    points_per_circle = 8
) -> bool:
    """
    Performs a tight spiral search around a GPS center point
    Stops if the camera detects a target.
    
    :return: True if a target is detected, otherwise False
    """
    radius = radius_step
    angle = 0.0

    while radius <= max_radius:
        angle_step = 2 * math.pi / points_per_circle

        for _ in range(points_per_circle):
            # Berechne Versatz in Metern
            offset_north = radius * math.cos(angle)
            offset_east = radius * math.sin(angle)

            # Konvertiere zu GPS
            wp_lat, wp_lon = offset_coordinates(center_lat, center_lon, offset_north, offset_east)

            print(f"📍 spiral point (r={radius:.1f} m, θ={math.degrees(angle):.1f}°) → ({wp_lat:.7f}, {wp_lon:.7f})")
            await drone.action.goto_location(wp_lat, wp_lon, target_altitude, 0)
            await asyncio.sleep(5)  # Wartezeit für Kamera

            if await check_camera_for_target():
                print("🎯 target detected during spiral flight.")
                return True

            angle += angle_step

        radius += radius_step

    print("❌ no target found in the tight spiral.")
    return False
