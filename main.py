from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify
from threading import Lock

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

# 初始化数据
data = {
    "presidential": {
        "candidates": [
            {"name": "唐子涵/吳亞旗", "votes": 0},
            {"name": "張璿婷/陳宣宇", "votes": 0},
            {"name": "鄭大邦/王宇彤", "votes": 0},
        ]
    },
    "legislative": {
        "areas": [
            {
                "area": "選區一",
                "candidates": [
                    {"name": "哈囉", "votes": 0},
                    {"name": "莊宸綾", "votes": 0},
                    {"name": "謝啟昱", "votes": 0},
                ],
            },
            {
                "area": "選區二",
                "candidates": [
                    {"name": "李雅淇", "votes": 0},
                    {"name": "賴成祐", "votes": 0},
                    {"name": "林哲豪", "votes": 0},
                ],
            },
            {
                "area": "選區三",
                "candidates": [
                    {"name": "王亭勻", "votes": 0},
                    {"name": "王喜樂", "votes": 0},
                    {"name": "王育晟", "votes": 0},
                ],
            },
            {
                "area": "選區四",
                "candidates": [
                    {"name": "葉依柔", "votes": 0},
                    {"name": "林士茵", "votes": 0},
                    {"name": "車秉逸", "votes": 0},
                ],
            },
        ]
    },
    "proportional": {
        "seats": {
            "建制派": {"seats": 0, "percentage": 0.0},
            "中間": {"seats": 0, "percentage": 0.0},
            "左派": {"seats": 0, "percentage": 0.0},
        },
        "total_seats": 10,
        "total_votes": 300,
        "registered_voters": 13452016,
    },
    "ticker_text": "投票時間結束 各開票所陸續回報狀態中",
    "display_mode": "presidential",
}

lock = Lock()


@app.route("/")
def control_panel():
    return render_template("control_panel.html", data=data)


@app.route("/update", methods=["POST"])
def update():
    with lock:
        election_type = request.form["election_type"]

        if election_type == "presidential":
            for i, candidate in enumerate(data["presidential"]["candidates"]):
                candidate["votes"] = int(request.form[f"presidential_{i}_votes"])

        elif election_type == "legislative":
            for area in data["legislative"]["areas"]:
                for i, candidate in enumerate(area["candidates"]):
                    candidate["votes"] = int(
                        request.form[f'{area["area"]}_candidate_{i}_votes']
                    )

        elif election_type == "proportional":
            for group in data["proportional"]["seats"]:
                data["proportional"]["seats"][group]["seats"] = int(
                    request.form[f"{group}_seats"]
                )
                data["proportional"]["seats"][group]["percentage"] = float(
                    request.form[f"{group}_percentage"]
                )
            data["proportional"]["total_seats"] = int(request.form["total_seats"])
            data["proportional"]["total_votes"] = int(request.form["total_votes"])
            data["proportional"]["registered_voters"] = int(
                request.form["registered_voters"]
            )

        elif election_type == "ticker":
            data["ticker_text"] = request.form["ticker_text"]

        elif election_type == "display_mode":
            data["display_mode"] = request.form["display_mode"]

    return redirect(url_for("control_panel"))


@app.route("/display")
def display():
    return render_template("display.html", data=data)


@app.route("/data")
def get_data():
    return jsonify(data)


if __name__ == "__main__":
    app.jinja_env.globals.update(enumerate=enumerate)
    app.run(debug=True)
