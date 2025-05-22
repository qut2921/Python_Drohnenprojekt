# webserver/server.py
from flask import Flask, request, render_template
import subprocess

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        mission = request.form.get("mission")
        landing_position = request.form.get("landingPosition", "")
        target_type = request.form.get("targetType", "")
        area = request.form.get("area", "")
        geofence = request.form.get("geofence", "")
        
        command = ["python3", "main.py", "--mission", mission, "--landingPosition", landing_position]
        
        if target_type:
            command += ["--targetType", target_type]
            
        if area:
            for line in area.splitlines():
                line = line.strip()
                if line:
                    command += ["--area", line]
                    
        if geofence:
            for line in geofence.splitlines():
                line = line.strip()
                if line:
                    command += ["--geofence", line]

        subprocess.Popen(command)

        return f"<h3>Mission {mission} gestartet mit Landing Position: {landing_position}</h3><a href='/'>Zurück</a>"

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)