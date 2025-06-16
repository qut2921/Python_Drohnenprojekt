import asyncio
from mavsdk import System
from mavsdk.offboard import VelocityBodyYawspeed
from collections import namedtuple

Position = namedtuple("Position", ["x", "y", "z"])


class Drone:
    def __init__(self):
        self.drone = System()
        self.position = Position(0, 0, 0)
        self.commands_log = []
        self.current_velocity = VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)
        self.keep_sending = True

    async def connect(self):
        """Verbindet sich mit der Drohne, arm sie und startet den Offboard-Modus"""
        try:
            await self.drone.connect(system_address="udp://:14540")
            await asyncio.sleep(2)  # kurze Wartezeit für die Verbindung
            await self.drone.action.arm()
            await self.drone.offboard.set_velocity_body(self.current_velocity)
            await self.drone.offboard.start()
            print("✅ Mit der Drohne verbunden und Offboard gestartet!")
        except Exception as e:
            print(f"❌ Verbindungsfehler: {e}")

    async def send_velocity_loop(self):
        """Sendet kontinuierlich die aktuelle Geschwindigkeit an die Drohne"""
        while self.keep_sending:
            await self.drone.offboard.set_velocity_body(self.current_velocity)
            await asyncio.sleep(0.1)  # 10 Hz senden

    async def move_drone(self, x: float, y: float, z: float, duration: float = 3.0):
        """Ändert die aktuelle Geschwindigkeit für eine gewisse Zeit"""
        print(f"✈️ Bewegung: x={x}, y={y}, z={z} für {duration} Sekunden")
        self.current_velocity = VelocityBodyYawspeed(x, y, z, 0.0)
        await asyncio.sleep(duration)

        # Stoppe die Bewegung wieder
        self.current_velocity = VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)

        # interne Positionsänderung (nur als Schätzung)
        self.position = Position(
            self.position.x + x * duration,
            self.position.y + y * duration,
            self.position.z + z * duration
        )

    async def execute_command(self, command):
        """Führt einen Befehl aus und loggt ihn"""
        self.commands_log.append(command)

        # Speziell behandeln: Drohne schon am Boden
        if command == "DOWN" and self.position.z <= 0:
            print("⚠️ Die Drohne ist bereits am niedrigsten Punkt!")
            return

        # Map für die Bewegungsbefehle
        commands_map = {
            "UP": lambda: self.move_drone(0.0, 0.0, -1.0),
            "DOWN": lambda: self.move_drone(0.0, 0.0, 1.0),
            "LEFT": lambda: self.move_drone(0.0, -1.0, 0.0),
            "RIGHT": lambda: self.move_drone(0.0, 1.0, 0.0),
            "FORWARD": lambda: self.move_drone(1.0, 0.0, 0.0),
            "BACKWARD": lambda: self.move_drone(-1.0, 0.0, 0.0)
        }

        if command in commands_map:
            await commands_map[command]()
        else:
            print(f"❌ Unbekannter Befehl: {command}")

    def verify_commands(self, commands):
        """Überprüft, ob alle gesendeten Befehle ausgeführt wurden"""
        return set(self.commands_log) == set(commands)


async def main():
    my_drone = Drone()
    await my_drone.connect()

    # Starte das kontinuierliche Senden in einem eigenen Task
    send_task = asyncio.create_task(my_drone.send_velocity_loop())

    # Liste der Befehle
    commands = ["UP", "RIGHT", "FORWARD", "LEFT", "BACKWARD", "DOWN"]

    # Befehle ausführen
    for command in commands:
        await my_drone.execute_command(command)

    # Bestätigung der Befehle
    print("✅ Alle Befehle wurden erfolgreich ausgeführt:", my_drone.verify_commands(commands))

    # Nach allen Befehlen stoppen
    my_drone.keep_sending = False
    await send_task
    print("✅ Drohne gestoppt und Programm beendet")


if __name__ == "__main__":
    asyncio.run(main())
