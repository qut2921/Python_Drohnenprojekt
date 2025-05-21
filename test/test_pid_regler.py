import control.controller_functions as cl  # type: ignore
import asyncio
import time
import matplotlib.pyplot as plt

# Initialwerte
x = 5.0  # Startposition (Fehler in m)
v = 0.0
dt = 0.1
steps = 500
# PID-Regler-Test: Parameter explizit setzen
state = {"integral": 0.0, "prev_error": 0.0}
kp, ki, kd = 0.8, 0.05, 0.1  # Hier bewusst übertrieben


# Logs für Plot
time_data = []
position_data = []
velocity_data = []

# Simulationsschleife
for t in range(steps):
    error = x
    v, state = cl.pid_update(error, dt, state, kp=kp, ki=ki, kd=kd, max_output=1.0)
    x -= v * dt

    time_data.append(t * dt)
    position_data.append(x)
    velocity_data.append(v)

# Plot
plt.plot(time_data, position_data, label="Position [m]")
plt.plot(time_data, velocity_data, label="Velocity [m/s]")
plt.xlabel("Time [s]")
plt.ylabel("Value")
plt.title("PID-Regler (Funktionsbasiert)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
