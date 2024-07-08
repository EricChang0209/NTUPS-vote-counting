from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
from threading import Lock
import json
import time
import threading

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
CORS(app)

DATA_FILE = "data.json"
lock = Lock()


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def auto_switch_display_mode():
    while True:
        with lock:
            data = load_data()
            if data["auto_display"] == "true":
                current_mode = data["display_mode"]
                next_mode = {
                    "presidential": "legislative",
                    "legislative": "proportional",
                    "proportional": "presidential",
                }[current_mode]
                data["display_mode"] = next_mode
                save_data(data)
        time.sleep(20)


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
            total_votes = data["presidential"]["total_votes"]
            for i, candidate in enumerate(data["presidential"]["candidates"]):
                candidate["votes"] = int(request.form[f"presidential_{i}_votes"])
                candidate["elected"] = f"presidential_{i}_elected" in request.form

            for candidate in data["presidential"]["candidates"]:
                candidate["percentage"] = round((candidate["votes"] / total_votes * 100), 1) if total_votes > 0 else 0

        elif election_type == "legislative":
            for area in data["legislative"]["areas"]:
                total_votes = area["total_votes"]
                for i, candidate in enumerate(area["candidates"]):
                    candidate["votes"] = int(request.form[f'{area["area"]}_candidate_{i}_votes'])
                    candidate["elected"] = f'{area["area"]}_candidate_{i}_elected' in request.form

                for candidate in area["candidates"]:
                    candidate["percentage"] = round((candidate["votes"] / total_votes * 100), 1) if total_votes > 0 else 0

        elif election_type == "proportional":
            total_votes = int(request.form["proportional_total_votes"])
            total_seats = int(request.form["proportional_total_seats"])
            seat_quota = total_votes / total_seats
            data["proportional"]["total_votes"] = total_votes
            data["proportional"]["total_seats"] = total_seats
            for group, details in data["proportional"]["seats"].items():
                details["votes"] = int(request.form[f'{group}_votes'])
                details["percentage"] = round((details["votes"] / total_votes * 100), 2) if total_votes > 0 else 0
                manual_seats = int(request.form.get(f"{group}_manual_seats", 0))
                if manual_seats > 0:
                    details["seats"] += manual_seats
                else:
                    details["seats"] = int(details["votes"] // seat_quota)

        elif election_type == "ticker":
            data["ticker_text"] = request.form["ticker_text"]

        elif election_type == "display_mode":
            form_display_mode = request.form["display_mode"]

            if form_display_mode == "auto":
                data["auto_display"] = "true"

            else:
                data["auto_display"] = "false"
                data["display_mode"] = request.form["display_mode"]

        save_data(data)
    return redirect(url_for("control_panel"))


@app.route("/display")
def display():
    return redirect("https://vote.ntupscamp.fun")


@app.route("/data")
def get_data():
    data = load_data()
    return jsonify(data)


if __name__ == "__main__":
    app.jinja_env.globals.update(enumerate=enumerate)
    app.run(debug=True, port=5050)
