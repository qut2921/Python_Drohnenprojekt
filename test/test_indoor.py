import asyncio
from mavsdk import system
from mavsdk.offboard import VelocityNedYaw
import control.controller_functions as cl
import control.logging as log
import utils.image_processing_raspi as ip


async def test_indoor():

    logfile = "test_indoor.log"
    log.log("Alignment gestartet", logfile)
    mission_id = 2

    drone = await cl.connect_drone(logfile)
    print("Warte auf Verbindung...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Verbunden mit Drohne!")
            break

    print("Warte auf lokale Positionsdaten...")
    async for health in drone.telemetry.health():
        if health.is_local_position_ok:
            print("Lokale Position bereit!")
            break

    
    vid = ip.start_videoCapture(2,logfile)
    color = 4  # orange target

    # Start indoor alignment test
    print("Alignment starten...")
    await cl.indoor_alignment_test(drone, vid, color, log)

    # Drohne schwebt weiterhin in der Luft
    while True:
        await drone.offboard.set_velocity_ned(VelocityNedYaw(0, 0, 0, 0))
        await asyncio.sleep(0.1)

asyncio.run(test_indoor())