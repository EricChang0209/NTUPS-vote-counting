from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
from threading import Lock
import json
import time
import threading

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
CORS(app)

DATA_FILE = 'data.txt'
lock = Lock()

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def auto_switch_display_mode():
    while True:
        with lock:
            data = load_data()
            if data['display_mode'] == 'auto':
                current_mode = data.get('current_auto_mode', 'presidential')
                next_mode = {
                    'presidential': 'legislative',
                    'legislative': 'proportional',
                    'proportional': 'presidential'
                }[current_mode]
                data['current_auto_mode'] = next_mode
                save_data(data)
        time.sleep(30)

threading.Thread(target=auto_switch_display_mode, daemon=True).start()

@app.route("/")
def control_panel():
    data = load_data()
    return render_template("control_panel.html", data=data)

@app.route("/update", methods=["POST"])
def update():
    with lock:
        data = load_data()
        election_type = request.form["election_type"]

        if election_type == "presidential":
            total_votes = 0
            for i, candidate in enumerate(data["presidential"]["candidates"]):
                candidate["votes"] = int(request.form[f"presidential_{i}_votes"])
                candidate["elected"] = f"presidential_{i}_elected" in request.form
                total_votes += candidate["votes"]
            data["presidential"]["total_votes"] = total_votes
            for candidate in data["presidential"]["candidates"]:
                candidate["percentage"] = (candidate["votes"] / total_votes * 100) if total_votes > 0 else 0

        elif election_type == "legislative":
            for area in data["legislative"]["areas"]:
                total_votes = 0
                for i, candidate in enumerate(area["candidates"]):
                    candidate["votes"] = int(request.form[f'{area["area"]}_candidate_{i}_votes'])
                    candidate["elected"] = f'{area["area"]}_candidate_{i}_elected' in request.form
                    total_votes += candidate["votes"]
                area["total_votes"] = total_votes
                for candidate in area["candidates"]:
                    candidate["percentage"] = (candidate["votes"] / total_votes * 100) if total_votes > 0 else 0

        elif election_type == "proportional":
            for group in data["proportional"]["seats"]:
                data["proportional"]["seats"][group]["percentage"] = float(request.form[f"{group}_percentage"])
            data["proportional"]["total_seats"] = int(request.form["total_seats"])
            data["proportional"]["total_votes"] = int(request.form["total_votes"])

        elif election_type == "ticker":
            data["ticker_text"] = request.form["ticker_text"]

        elif election_type == "display_mode":
            data["display_mode"] = request.form["display_mode"]
            if data["display_mode"] != "auto" and "current_auto_mode" in data:
                del data["current_auto_mode"]

        save_data(data)
    return redirect(url_for("control_panel"))

@app.route("/display")
def display():
    data = load_data()
    return render_template("display.html", data=data)

@app.route("/data")
def get_data():
    data = load_data()
    return jsonify(data)

if __name__ == "__main__":
    app.jinja_env.globals.update(enumerate=enumerate)
    app.run(debug=True, port=5050)
