from flask import Flask, jsonify, request

app = Flask(__name__)

PROGRAMS = {
    "Fat Loss (FL)": {"factor": 22, "workout": "Squat, cardio, bench, deadlift, recovery"},
    "Muscle Gain (MG)": {"factor": 35, "workout": "Squat, bench, deadlift, press, rows"},
    "Beginner (BG)": {"factor": 26, "workout": "Air squats, ring rows, push-ups"},
}

GYM = {"capacity": 150, "area_sq_ft": 10000, "break_even_members": 250}

clients = []


def estimate_calories(weight_kg, program):
    if program not in PROGRAMS:
        raise ValueError("Unknown program")
    if weight_kg <= 0:
        raise ValueError("Weight must be positive")
    return int(weight_kg * PROGRAMS[program]["factor"])


@app.get("/")
def home():
    return jsonify({"service": "ACEest Fitness & Gym", "gym": GYM})


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/programs")
def list_programs():
    return jsonify([
        {"name": name, "factor": data["factor"], "workout": data["workout"]}
        for name, data in PROGRAMS.items()
    ])


@app.post("/calories")
def calories():
    body = request.get_json(silent=True) or {}
    try:
        kcal = estimate_calories(float(body["weight"]), body["program"])
    except (KeyError, TypeError, ValueError) as exc:
        return jsonify({"error": str(exc) or "Invalid input"}), 400
    return jsonify({"program": body["program"], "calories": kcal})


@app.post("/clients")
def add_client():
    body = request.get_json(silent=True) or {}
    name = (body.get("name") or "").strip()
    program = body.get("program")
    if not name or program not in PROGRAMS:
        return jsonify({"error": "Name and a valid program are required"}), 400
    try:
        weight = float(body.get("weight", 0))
        kcal = estimate_calories(weight, program)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    record = {
        "name": name,
        "age": body.get("age"),
        "weight": weight,
        "program": program,
        "calories": kcal,
    }
    clients.append(record)
    return jsonify(record), 201


@app.get("/clients")
def list_clients():
    return jsonify(clients)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
