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
        
        command = ["python3", "main.py", "--mission", mission, "--landingPosition", landing_position]
        
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

        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout + result.stderr

    return render_template("index.html", output=output)

@app.route("/logs")
def get_logs():
    try:
        with open("logs/mission.log", "r") as f:
            log_content = f.read()
    except Exception as e:
        log_content = f"Fehler beim Lesen der Log-Datei: {str(e)}"
    return log_content

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)