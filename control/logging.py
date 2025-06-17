import asyncio
from datetime import datetime


def log(message, logfile="default.log"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(logfile, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)


async def monitor(drone):
    log("Logger gestartet. Warte auf Telemetrie...")

    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            break
    log("GPS und Home-Position bereit.")

    home = await drone.telemetry.home().__anext__()
    home_position = (home.latitude_deg, home.longitude_deg)
    log(f"Startposition gespeichert: {home_position}")

    async for position in drone.telemetry.position():
        if position.fix_type < 3:
            log("FEHLER: GPS-Fix verloren oder unzureichend")
        await asyncio.sleep(0.5)


async def monitor_battery(drone):
    async for battery in drone.telemetry.battery():
        if battery.remaining_percent < 0.15:
            log(f"WARNUNG: Batterie schwach ({battery.remaining_percent * 100:.0f}%)")
        await asyncio.sleep(1.0)


async def monitor_rc_connection(drone):
    async for rc_status in drone.telemetry.rc_status():
        if not rc_status.is_available:
            log("FEHLER: Verbindung zur Fernsteuerung verloren!")
        await asyncio.sleep(1.0)
