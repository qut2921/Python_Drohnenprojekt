import asyncio
from mavsdk import System
from mavsdk.telemetry import Position, Health
from datetime import datetime
import math


class MavsdkErrorLogger:
    def __init__(self):
        self.log_file = "mavsdk_errors.log"
        self.max_altitude = 15  # Meter
        self.geofence_radius = 100  # Meter
        self.home_position = None  # (lat, lon)

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
        print(f"[{timestamp}] {message}")

    def _distance(self, lat1, lon1, lat2, lon2):
        R = 6371000  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2) ** 2
            + math.cos(phi1)
            * math.cos(phi2)
            * math.sin(delta_lambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    async def monitor(self):
        drone = System()
        await drone.connect(system_address="udp://:14540")

        self.log("Logger gestartet. Warte auf Telemetrie...")

        async for health in drone.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                break
        self.log("GPS und Home-Position bereit.")

        async for position in drone.telemetry.position():
            if position.fix_type < 3:
                self.log("FEHLER: GPS-Fix verloren oder unzureichend")

            if not self.home_position:
                self.home_position = (
                    position.latitude_deg,
                    position.longitude_deg,
                )
                self.log(
                    f"Startposition gespeichert: {self.home_position}"
                )
                continue

            if position.relative_altitude_m > self.max_altitude:
                self.log(
                    f"FEHLER: Flughöhe überschritten "
                    f"({position.relative_altitude_m:.1f} m)"
                )

            current_pos = (
                position.latitude_deg,
                position.longitude_deg,
            )
            dist = self._distance(*self.home_position, *current_pos)
            if dist > self.geofence_radius:
                self.log(
                    f"FEHLER: Geofence verletzt "
                    f"({dist:.1f} m vom Startpunkt)"
                )

    async def monitor_battery(self):
        drone = System()
        await drone.connect(system_address="udp://:14540")

        async for battery in drone.telemetry.battery():
            if battery.remaining_percent < 0.15:
                self.log(
                    f"WARNUNG: Batterie schwach "
                    f"({battery.remaining_percent * 100:.0f}%)"
                )


async def main():
    logger = MavsdkErrorLogger()
    await asyncio.gather(
        logger.monitor(),
        logger.monitor_battery(),
    )


if __name__ == "__main__":
    asyncio.run(main())
