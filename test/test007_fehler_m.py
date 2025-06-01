import asyncio
from mavsdk import System
from mavsdk.offboard import VelocityBodyYawspeed
from collections import namedtuple

# Namedtuple für die Position anstatt eine Liste zu erstellen 

Position = namedtuple("Position", ["x", "y", "z"])


class Drone:
    def __init__(self):
        self.drone = System()
        self.position = Position(0, 0, 0)
        self.commands_log = []

    async def connect(self):
        """Verbindet sich mit der Drohne und startet den Offboard-Modus"""
        try:
            await self.drone.connect(system_address="udp://:14540")
            await self.drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
            await self.drone.offboard.start()
            print("Mit der Drohne verbunden!")
        except Exception as e:
            print(f" Verbindungsfehler !!! : {e}")

    async def move_drone(self, x: float, y: float, z: float):
        """Bewegt die Drohne basierend auf den angegebenen Geschwindigkeiten"""
        print(f"Bewegung: x={x}, y={y}, z={z}")
        await self.drone.offboard.set_velocity_body(VelocityBodyYawspeed(x, y, z, 0.0))
        await asyncio.sleep(3)
        self.position = Position(self.position.x + x, self.position.y + y, self.position.z + z)

    async def execute_command(self, command):
        """Führt einen Befehl für die Drohne aus"""
        self.commands_log.append(command)

        commands_map = {
            "UP": lambda: self.drone.action.takeoff(),
            "DOWN": lambda: self.drone.action.land() if self.position.z > 0 else print(" Die Drohne ist bereits am niedrigsten Punkt ! "),
            "LEFT": lambda: self.move_drone(0.0, -1.0, 0.0),
            "RIGHT": lambda: self.move_drone(0.0, 1.0, 0.0),
            "FORWARD": lambda: self.move_drone(1.0, 0.0, 0.0),
            "BACKWARD": lambda: self.move_drone(-1.0, 0.0, 0.0)
        }

        if command in commands_map:
            await commands_map[command]()
        else:
            print(f"Unbekannter Befehl: {command}")

    def verify_commands(self, commands):
        """Überprüft, ob die gesendeten Befehle korrekt ausgeführt wurden"""
        return set(self.commands_log) == set(commands)


async def main():
    my_drone = Drone()
    await my_drone.connect()

    # Liste der Befehle
    commands = ["UP", "RIGHT", "FORWARD", "LEFT", "BACKWARD", "DOWN"]

    # Befehle ausführen
    for command in commands:
        await my_drone.execute_command(command)

    # Bestätigung der Befehle
    print("Die Befehle wurden erfolgreich ausgeführt:", my_drone.verify_commands(commands))


asyncio.run(main())
