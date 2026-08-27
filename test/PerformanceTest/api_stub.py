"""
Fase C - API local minimo para medir performance de lectura/escritura en DynamoDB.

No es el microservicio de validacion completo (eso es una fase de implementacion
de computo aparte, no cubierta en esta actividad). Es un arnes de medicion:
aisla exactamente las dos operaciones de DynamoDB que la Actividad 1 pide medir
("consumo de lectura y/o escritura"), sin la logica de negocio completa de CU-03,
para que JMeter mida la latencia real de GetItem/PutItem contra la tabla.

Endpoints:
  GET  /cards/<card_id>   -> Lectura (GetItem sobre Cards, PK=cardId)
  POST /validations       -> Escritura (PutItem sobre ValidationLog, PK=cardId, SK=timestamp)

Uso:
    AWS_PROFILE=estebangaca python3 api_stub.py
    # sirve en http://127.0.0.1:5001
"""

import os
import time
import uuid
from datetime import datetime, timedelta, timezone

import boto3
from flask import Flask, jsonify, request

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
AWS_PROFILE = os.environ.get("AWS_PROFILE")

session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
dynamodb = session.resource("dynamodb")
cards_table = dynamodb.Table("Cards")
validation_log_table = dynamodb.Table("ValidationLog")

app = Flask(__name__)


@app.get("/cards/<card_id>")
def get_card(card_id):
    """Lectura: GetItem por Partition Key (camino critico de validacion)."""
    t0 = time.perf_counter()
    resp = cards_table.get_item(Key={"cardId": card_id})
    elapsed_ms = (time.perf_counter() - t0) * 1000
    item = resp.get("Item")
    if not item:
        return jsonify({"error": "not_found", "cardId": card_id}), 404
    return jsonify({"item": item, "dynamodb_ms": round(elapsed_ms, 2)}), 200


@app.post("/validations")
def post_validation():
    """Escritura: PutItem en ValidationLog (evento de validacion)."""
    body = request.get_json(force=True, silent=True) or {}
    card_id = body.get("cardId", f"CARD-{uuid.uuid4().hex[:8]}")
    device_id = body.get("deviceId", "PERF-TEST-DEVICE")
    device_type = body.get("deviceType", "STATION")

    now = datetime.now(timezone.utc)
    item = {
        "cardId": card_id,
        "timestamp": now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        "deviceId": device_id,
        "deviceType": device_type,
        "result": "ALLOW",
        "reasonCode": "OK",
        "balanceAfter": 0,
        "ttl": int((now + timedelta(days=400)).timestamp()),
    }

    t0 = time.perf_counter()
    validation_log_table.put_item(Item=item)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    return jsonify({"item": item, "dynamodb_ms": round(elapsed_ms, 2)}), 201


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001)
