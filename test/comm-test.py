from pymavlink import mavutil
import time

def connect_to_pixhawk(port='/dev/ttyACM0', baudrate=57600):
    """
    Verbindet sich mit dem Pixhawk über MAVLink.
    :param port: z. B. '/dev/ttyACM0' für USB-Verbindung
    :param baudrate: Standard ist 57600
    :return: MAVLink-Verbindung
    """
    print(f"Verbinde zu Pixhawk über {port} mit Baudrate {baudrate}...")
    connection = mavutil.mavlink_connection(port, baud=baudrate)

    print("Warte auf Heartbeat...")
    connection.wait_heartbeat()
    print(f"Heartbeat empfangen – System ID: {connection.target_system}, Komponente: {connection.target_component}")
    return connection

def arm_drone(connection):
    """
    Sendet ARM-Befehl an den Flugcontroller.
    """
    print("Sende ARM-Befehl...")
    connection.mav.command_long_send(
        connection.target_system,
        connection.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        1, 0, 0, 0, 0, 0, 0  # 1 = ARM, 0 = DISARM
    )
    print("ARM-Befehl gesendet.")

def read_altitude(connection):
    """
    Liest die Höhe aus GLOBAL_POSITION_INT MAVLink-Meldung.
    """
    print("Warte auf Telemetriedaten (GLOBAL_POSITION_INT)...")
    msg = connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=5)
    if msg:
        altitude = msg.relative_alt / 1000.0  # Höhe in Metern
        print(f"Aktuelle Höhe: {altitude:.2f} m")
    else:
        print("Keine Telemetriedaten empfangen.")

if __name__ == '__main__':
    # Hier kann man später /dev/serial0 für UART nutzen
    connection = connect_to_pixhawk(port='/dev/ttyACM0')
    arm_drone(connection)
    read_altitude(connection)