
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
import json
import os
import re

app = Flask(__name__)

# Archivo local para los registros de la simulación
DATA_FILE = Path(__file__).parent / "registros.json"
file_lock = Lock()


def guardar_registro(registro):
    """Guarda solamente identificadores ficticios y eventos."""
    with file_lock:
        try:
            if DATA_FILE.exists():
                with DATA_FILE.open("r", encoding="utf-8") as archivo:
                    registros = json.load(archivo)
                if not isinstance(registros, list):
                    registros = []
            else:
                registros = []

            registros.append(registro)

            with DATA_FILE.open("w", encoding="utf-8") as archivo:
                json.dump(registros, archivo, ensure_ascii=False, indent=2)

            return True
        except (OSError, json.JSONDecodeError):
            app.logger.exception("No se pudo guardar el registro")
            return False


@app.get("/")
def inicio():
    return render_template("index.html")


@app.post("/event")
def registrar_evento():
    datos = request.get_json(silent=True) or {}

    # Solo aceptamos identificadores ficticios y eventos permitidos.
    usuario = str(datos.get("usuario", "")).strip()
    evento = str(datos.get("evento", ""))

    if not re.fullmatch(r"demo_[a-zA-Z0-9_-]{1,30}", usuario):
        return jsonify({
            "ok": False,
            "error": "Usa un identificador ficticio como demo_estudiante"
        }), 400

    if evento not in ("visita", "prueba_completada"):
        return jsonify({"ok": False, "error": "Evento no válido"}), 400

    registro = {
        "usuario_demo": usuario,
        "evento": evento,
        "fecha_utc": datetime.now(timezone.utc).isoformat()
    }

    if not guardar_registro(registro):
        return jsonify({
            "ok": False,
            "error": "No se pudo guardar el registro"
        }), 500

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
