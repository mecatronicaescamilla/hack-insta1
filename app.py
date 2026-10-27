
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timezone
from collections import Counter
from threading import Lock
import os

app = Flask(__name__)
events = []
lock = Lock()

@app.get("/")
def home():
    record_event("visit")
    return render_template("index.html")

@app.post("/event")
def event():
    data = request.get_json(silent=True) or {}
    kind = data.get("type")

    if kind not in ("demo_submit", "training_complete"):
        return jsonify({"error": "Evento no válido"}), 400

    record_event(kind)
    return jsonify({"ok": True})

@app.get("/admin")
def admin():
    # Panel básico de demostración.
    # Añade autenticación antes de usarlo en público.
    with lock:
        snapshot = list(events)

    return jsonify({
        "total": len(snapshot),
        "events": snapshot[-100:],
        "counts": dict(Counter(e["type"] for e in snapshot))
    })

def record_event(kind):
    with lock:
        events.append({
            "type": kind,
            "time": datetime.now(timezone.utc).isoformat()
        })

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
