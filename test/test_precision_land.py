# test_precision_land.py

import asyncio
from mavsdk import System
from mavsdk.offboard import PositionNedYaw
import modules.controller_functions as cl
import random

class DummyImageProcessing:
    def __init__(self):
        self.x = 0.6
        self.y = -0.4

    def get_target_offset(self):
        # Simulate reducing offset (x/y → 0)
        if abs(self.x) > 0.05:
            self.x *= 0.8
        else:
            self.x = 0.0
        if abs(self.y) > 0.05:
            self.y *= 0.8
        else:
            self.y = 0.0
        return self.x, self.y

async def run():
    drone = System()
     # 1 ️ Connect to the drone
    drone = await cl.connect_drone()

    # 2  User confirmation before arming
    while True:
        user_input = input(
            "🚦 Ready to arm and start mission? (y/n): ").strip().lower()
        if user_input == "y":
            break
        elif user_input == "n":
            print("❌ Mission aborted by user.")
            exit(0)
        else:
            print("⚠️ Please enter 'y' to start or 'n' to abort.")

    # 3 ️ Arm the drone
    await cl.arm_drone(drone)
    await asyncio.sleep(2)

    # 4  User confirmation before arming
    while True:
        user_input = input(
            "🚦 Ready to arm and start mission? (y/n): ").strip().lower()
        if user_input == "y":
            break
        elif user_input == "n":
            print("❌ Mission aborted by user.")
            exit(0)
        else:
            print("⚠️ Please enter 'y' to start or 'n' to abort.")

    # 5  Take off to the first altitude
    await cl.default_takeoff(drone, 5)
    await asyncio.sleep(2)

    # 6  Precision landing test
    print("🚀 Ready for precision landing test")
    image_processing = DummyImageProcessing()
    await cl.precision_land(drone, image_processing)

if __name__ == "__main__":
    asyncio.run(run())
