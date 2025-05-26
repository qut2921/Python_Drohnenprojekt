import asyncio
from mavsdk import System
from mavsdk.telemetry import Position, Health
from datetime import datetime

class MavsdkErrorLogger:
    def __init__(self):
        self.log_file = "/media/aviator/ITENSO/mavsdk_errors.log"
        self.home_position = None  # (lat, lon)

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
        print(f"[{timestamp}] {message}")

    async def monitor(self, drone: System):
        self.log("Logger gestartet. Warte auf Telemetrie...")

        # Warte auf gültiges GPS und Home-Position
        async for health in drone.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                break
        self.log("GPS und Home-Position bereit.")

        # Hole Startposition von Home-Position (wie in goto_location)
        home = await drone.telemetry.home().__anext__()
        self.home_position = (home.latitude_deg, home.longitude_deg)
        self.log(f"Startposition gespeichert: {self.home_position}")

        # Überwache GPS-Fix
        async for position in drone.telemetry.position():
            if position.fix_type < 3:
                self.log("FEHLER: GPS-Fix verloren oder unzureichend")
            await asyncio.sleep(0.5)

    async def monitor_battery(self, drone):
        async for battery in drone.telemetry.battery():
            if battery.remaining_percent < 0.15:
                self.log(
                    f"WARNUNG: Batterie schwach "
                    f"({battery.remaining_percent * 100:.0f}%)"
                )
            await asyncio.sleep(1.0)

    async def monitor_rc_connection(self, drone):
        async for rc_status in drone.telemetry.rc_status():
            if not rc_status.is_available:
                self.log("FEHLER: Verbindung zur Fernsteuerung verloren!")
            await asyncio.sleep(1.0)


async def main():
    logger = MavsdkErrorLogger()
    drone = await cl.connect_drone()  # Nutzt deine eigene Funktion zum Verbinden

    await asyncio.gather(
        logger.monitor(drone),
        logger.monitor_battery(drone),
        logger.monitor_rc_connection(drone),
    )


if __name__ == "__main__":
    asyncio.run(main())



