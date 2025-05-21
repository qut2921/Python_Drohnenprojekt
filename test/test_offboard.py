import asyncio
from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed)
import modules.error_message as em

async def run():
    drone = System()
    await drone.connect(system_address="serial:///dev/ttyAMA0:57600")
    #await drone.connect(system_address="udp://:14540")
    print("Warte auf Verbindung...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Verbunden mit Drohne!")
            break

    print("Warte auf erste Positionsdaten...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("GPS bereit!")
            break

    print("Sende ersten Dummy-Setpoint...")
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))

    print("Starte Offboard-Modus...")
    try:
        await drone.offboard.start()
        print("Offboard-Modus aktiviert")
    except OffboardError as error:
        message = f"Offboard-Modus konnte nicht aktiviert werden: {error._result.result}"
        print(message)
        em.log(message)
        message = "--> breche ab"
        print(message)
        em.log(message)
        print(f"Offboard-Modus konnte nicht aktiviert werden: {error._result.result}")
        print("--> breche ab")
        return

    while True:
        await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(run())