import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio
from mavsdk import system
from mavsdk.offboard import VelocityNedYaw
import control.controller_functions as cl
import control.logging as log
import utils.image_processing_raspi as ip

async def test_indoor_prep():

    logfile = "test_indoor_prep.log"
    log.log("Alignment gestartet", logfile)
    mission_id = 1

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

    
    vid = ip.start_videoCapture(mission_id,logfile)
    color = 4  # orange target
    sequence = 0
    
    # Start indoor image capture
    print("Image Capture starten...")
    await ip.main_mission_1(drone,vid,sequence)
    print("Image Capture abgeschlossen.")
    sequence=+1
    print("Image Capture starten...")
    await ip.main_mission_1(drone,vid,sequence)
    print("Image Capture abgeschlossen.")

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

    
    vid = ip.start_videoCapture(2, logfile)
    color = 4  # orange target

    # Start indoor alignment test
    try:
        print("Alignment starten...")
        await cl.indoor_alignment_test(drone, vid, color, log)
    except Exception as e:
        print(f"Fehler beim Indoor-Alignment-Test: {e}")
        print("Versuche, die Drohne zu landen...")
        await drone.action.land()
        print("Drohne gelandet.")

    # 3s warten, um die Drohne zu stabilisieren
    t = 0.0
    while t < 3.0:
        print(f"Warte {3 - t} Sekunden...")
        await drone.offboard.set_velocity_ned(VelocityNedYaw(0, 0, 0, 0))
        await asyncio.sleep(0.1)
        t += 0.1

    # Drohne versucht zu landen
    try:
        print("Drohne soll landen...")
        await drone.action.land()
    except Exception as e:
        print(f"Fehler beim Landen: {e}")
    print("Drohne gelandet.")

#asyncio.run(test_indoor())
asyncio.run(test_indoor_prep())