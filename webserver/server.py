# webserver/server.py
from flask import Flask, request, render_template
import subprocess

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    if request.method == "POST":
        mission = request.form.get("mission")
        landing_position = request.form.get("landingPosition", "")
        target_type = request.form.get("targetType", "")
        area = request.form.get("area", "")
        geofence = request.form.get("geofence", "")
        target_number = request.form.get("targetNumber", "")   # Neuer Parameter
        waypoints = request.form.get("waypoints", "")

        command = ["python3", "Desktop/Python_Drohnenprojekt/main.py", "--mission", mission, "--landingPosition", landing_position]
        
        if target_number:
            command += ["--targetNumber", target_number]

        if target_type:
            command += ["--targetType", target_type]

        if area:
            # Join all lines into one string with spaces between coordinates
            normalized_area = " ".join(line.strip() for line in area.splitlines() if line.strip())
            command += ["--area", normalized_area]
      
        if geofence:
            normalized_geofence = " ".join(line.strip() for line in geofence.splitlines() if line.strip())
            command += ["--geofence", normalized_geofence]

        if waypoints:
            normalized_waypoints = " ".join(line.strip() for line in waypoints.splitlines() if line.strip())
            command += ["--waypoints", normalized_waypoints]

        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout + result.stderr

    return render_template("index.html", output=output)

@app.route("/logs/mission1")
def get_logs1():
    try:
        with open("logs/mission1.log", "r") as f:
            log_content = f.read()
    except Exception as e:
        log_content = f"Fehler beim Lesen der Log-Datei: {str(e)}"
    return log_content

@app.route("/logs/mission2")
def get_logs2():
    try:
        with open("logs/mission2.log", "r") as f:
            log_content = f.read()
    except Exception as e:
        log_content = f"Fehler beim Lesen der Log-Datei: {str(e)}"
    return log_content

@app.route("/logs/mission3")
def get_logs3():
    try:
        with open("logs/mission3.log", "r") as f:
            log_content = f.read()
    except Exception as e:
        log_content = f"Fehler beim Lesen der Log-Datei: {str(e)}"
    return log_content

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)