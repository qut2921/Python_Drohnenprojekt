import asyncio
from mavsdk import System

class Drone:
    def __init__(self):
        self.drone = System()
        self.position = [0, 0, 0]  # x, y, z-Koordinaten
        self.commands_log = []

    async def connect(self):
        """Verbindet sich mit der Drohne"""
        await self.drone.connect(system_address="udp://:14540")
        print("Drohne verbunden!")
print (" ")
    async def execute_command(self, command):
        """Führt einen Befehl aus und speichert ihn im Log"""
        self.commands_log.append(command)

        if command == "UP":
            print("Die Drohne Steigt auf...")
            await self.drone.action.takeoff()
            await asyncio.sleep(5)
            self.position[2] += 1

        elif command == "DOWN" and self.position[2] != 0:
            print("Die Drohne steigt ab und wird vielleicht landen...")
            await self.drone.action.land()
            await asyncio.sleep(5)
            self.position[2] -= 1

        elif command == "DOWN" and self.position[2] == 0:
            print("Die Drohne ist bereits am niedrigsten Punkt!")

        elif command == "LEFT":
            print("Die Drohne Bewegt sich nach links...")
            await self.drone.offboard.set_velocity_body(
                mavsdk.offboard.VelocityBodyYawspeed(0.0, -1.0, 0.0, 0.0)
            )
            await asyncio.sleep(3)
            self.position[1] -= 1

        elif command == "RIGHT":
            print("Die Drohne Bewegt sich nach rechts...")
            await self.drone.offboard.set_velocity_body(
                mavsdk.offboard.VelocityBodyYawspeed(0.0, 1.0, 0.0, 0.0)
            )
            await asyncio.sleep(3)
            self.position[1] += 1

        elif command == "FORWARD":
            print("Bewegt sich vorwärts...")
            await self.drone.offboard.set_velocity_body(
                mavsdk.offboard.VelocityBodyYawspeed(1.0, 0.0, 0.0, 0.0)
            )
            await asyncio.sleep(3)
            self.position[0] += 1

        elif command == "BACKWARD":
            print("Bewegt sich rückwärts...")
            await self.drone.offboard.set_velocity_body(
                mavsdk.offboard.VelocityBodyYawspeed(-1.0, 0.0, 0.0, 0.0)
            )
            await asyncio.sleep(3)
            self.position[0] -= 1

    def verify_commands(self, commands):
        """Überprüft, ob alle Befehle korrekt ausgeführt wurden"""
        return self.commands_log == commands


async def main():
    my_drone = Drone()
    await my_drone.connect()

    await my_drone.execute_command("UP")
    await my_drone.execute_command("RIGHT")
    await my_drone.execute_command("FORWARD")
    await my_drone.execute_command("LEFT")
    await my_drone.execute_command("BACKWARD")
    await my_drone.execute_command("DOWN")

    print("Befehle erfolgreich ausgeführt :", my_drone.verify_commands(["UP", "RIGHT", "FORWARD", "LEFT", "BACKWARD", "DOWN"]))


asyncio.run(main())
