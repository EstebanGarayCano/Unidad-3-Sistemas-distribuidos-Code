"""
Fase B - Generacion y carga de registros ficticios (SITP - CU-03).

Carga datos en las 4 tablas definidas en Terraform (infra/dynamodb):
Cards, Blacklist, Whitelist, ValidationLog.

Dos opciones parametrizadas de generacion (requisito: "al menos 2 opciones"):

  --modo sintetico     Datos totalmente aleatorios (sin referencia a lugares reales).
  --modo transmilenio  Usa nombres reales de portales/troncales de TransMilenio
                        (fuente: datosabiertos-transmilenio.hub.arcgis.com, ya
                        citada en la seccion 1 del documento) para el campo
                        deviceId de las validaciones en estacion.

--count controla el numero de tarjetas (Cards) generadas; por defecto 15000,
el minimo exigido por la guia de actividades. Los registros de ValidationLog,
Blacklist y Whitelist se derivan de esa cantidad con proporciones realistas
(ver README.md de esta carpeta para la justificacion de cada proporcion).

Uso:
    python fase_b_carga_datos.py --profile sitp-sandbox --modo transmilenio
    python fase_b_carga_datos.py --profile sitp-sandbox --modo sintetico --count 50000
    python fase_b_carga_datos.py --dry-run --count 100          # sin AWS, solo prueba local
    python fase_b_carga_datos.py --endpoint-url http://localhost:8000 --count 1000  # DynamoDB Local
"""

import argparse
import random
import time
import uuid
from datetime import datetime, timedelta, timezone

import boto3

TABLE_CARDS = "Cards"
TABLE_BLACKLIST = "Blacklist"
TABLE_WHITELIST = "Whitelist"
TABLE_VALIDATION_LOG = "ValidationLog"

CARD_TYPE_WEIGHTS = [
    ("CIUDADANO_PERSONALIZADA", 0.55),
    ("CIUDADANO_ANONIMA", 0.20),
    ("SUBSIDIADO", 0.13),
    ("FUNCIONARIO_BUS", 0.05),
    ("FUNCIONARIO_SITP", 0.04),
    ("EMERGENCIA", 0.03),
]
WHITELIST_TYPES = {"FUNCIONARIO_BUS", "FUNCIONARIO_SITP", "EMERGENCIA"}

# Portales/troncales reales de TransMilenio (fuente: Guia General de Viaje,
# corte dic-2025, y datosabiertos-transmilenio.hub.arcgis.com). Se usan solo
# como referencia de nombre de dispositivo/estacion en modo "transmilenio".
PORTALES_REALES = [
    "Portal Norte", "Portal Suba", "Portal 80", "Portal Américas",
    "Portal Sur", "Portal Usme", "Portal Tunal", "Portal 20 de Julio",
    "Portal Eldorado",
]
ESTACIONES_REALES = [
    "Calle 100", "Héroes", "Museo Nacional", "Av. Jiménez", "Calle 72",
    "Marly", "Ricaurte", "Restrepo", "Banderas", "Alcalá", "CAD",
    "Universidades", "Av. Chile", "Polo", "Molinos", "Santa Lucía",
]
ZONAS_BUS = ["SUBA", "USME", "FONTIBON", "KENNEDY", "ENGATIVA", "BOSA", "CHAPINERO"]

REASON_CODES_DENY = ["BLACKLISTED", "TOO_SOON", "CARD_EXPIRED", "NOT_WHITELISTED", "INSUFFICIENT_BALANCE"]


def now_utc():
    return datetime.now(timezone.utc)


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def weighted_choice(weights):
    r = random.random()
    acc = 0.0
    for value, w in weights:
        acc += w
        if r <= acc:
            return value
    return weights[-1][0]


def gen_card_id(seq):
    return f"CARD-{seq:08d}"


def gen_user_id():
    return f"CC-{random.randint(1_000_000_000, 1_099_999_999)}"


def gen_device_id(modo, device_type):
    if device_type == "STATION":
        if modo == "transmilenio":
            nombre = random.choice(PORTALES_REALES + ESTACIONES_REALES)
            return nombre.upper().replace(" ", "-").replace(".", "")
        return f"STATION-{random.randint(1, 138):03d}"
    else:  # BUS
        if modo == "transmilenio":
            zona = random.choice(ZONAS_BUS)
            return f"BUS-{zona}-{random.randint(0, 9999):04d}"
        return f"BUS-{random.randint(0, 7393):04d}"


def build_card(seq, ttl_days):
    card_type = weighted_choice(CARD_TYPE_WEIGHTS)
    card_id = gen_card_id(seq)
    issued = now_utc() - timedelta(days=random.randint(0, 8 * 365))
    expiration = issued + timedelta(days=10 * 365)
    last_validation = now_utc() - timedelta(minutes=random.randint(1, 60 * 24 * 30))

    item = {
        "cardId": card_id,
        "cardType": card_type,
        "status": "ACTIVE" if random.random() > 0.02 else "EXPIRED",
        "expirationDate": expiration.strftime("%Y-%m-%d"),
        "lastValidationAt": iso(last_validation),
    }

    if card_type != "CIUDADANO_ANONIMA":
        item["userId"] = gen_user_id()  # sparse: omitido en anonimas -> no aparece en el GSI

    if card_type in ("CIUDADANO_PERSONALIZADA", "CIUDADANO_ANONIMA", "SUBSIDIADO"):
        item["balance"] = random.randint(0, 50_000)
    else:
        item["consumptionParams"] = {
            "freeTripsPerDay": random.choice([2, 4, 10]),
            "usedToday": random.randint(0, 2),
        }

    return item, card_type, card_id


def build_blacklist(card_id, user_id):
    reason = weighted_choice([("LOST", 0.40), ("STOLEN", 0.35), ("FRAUD", 0.25)])
    if reason == "FRAUD":
        status = weighted_choice([("ACTIVE", 0.7), ("PENDING_AUTHORIZATION", 0.3)])
    else:
        status = "ACTIVE"

    item = {
        "cardId": card_id,
        "reason": reason,
        "status": status,
        "reportedBy": user_id or "SISTEMA-FRAUDE",
        "verifiedBy": f"FUNC-{random.randint(0, 9999):04d}",
        "addedAt": iso(now_utc() - timedelta(days=random.randint(0, 180))),
    }
    if reason == "FRAUD" and status == "ACTIVE":
        item["authorizedBy"] = f"TM-AUTH-{random.randint(1000, 9999)}"
    return item


def build_whitelist(card_id, card_type):
    return {
        "cardId": card_id,
        "cardType": card_type,
        "consumptionParams": {"freeTripsPerDay": random.choice([4, 10])},
        "sourceReport": f"ENTE-GESTOR-RPT-{random.randint(1000, 9999)}",
        "addedAt": iso(now_utc() - timedelta(days=random.randint(0, 365))),
    }


def build_validation_logs(card_id, card_type, is_blacklisted, modo, ttl_days, n_events):
    items = []
    # Timestamp acumulativo (cada evento = el anterior + un offset positivo):
    # garantiza unicidad de la Sort Key sin depender del azar. La version
    # anterior (base + k*offset_aleatorio) podia producir el mismo timestamp
    # para dos eventos del mismo card_id cuando offset1 == 2*offset2,
    # causando "Provided list of keys contains duplicates" en BatchWriteItem.
    ts = now_utc() - timedelta(days=random.randint(0, 30))
    for k in range(n_events):
        ts = ts + timedelta(seconds=random.randint(30, 600))
        device_type = weighted_choice([("STATION", 0.45), ("BUS", 0.55)])

        if is_blacklisted and random.random() < 0.6:
            result, reason_code = "DENY", "BLACKLISTED"
        elif random.random() < 0.03:
            result, reason_code = "DENY", random.choice(REASON_CODES_DENY)
        else:
            result, reason_code = "ALLOW", "OK"

        items.append({
            "cardId": card_id,
            "timestamp": iso(ts),
            "deviceId": gen_device_id(modo, device_type),
            "deviceType": device_type,
            "result": result,
            "reasonCode": reason_code,
            "balanceAfter": random.randint(0, 50_000),
            "ttl": int((now_utc() + timedelta(days=ttl_days)).timestamp()),
        })
    return items


def write_batch(table, items, dry_run, counters, key):
    counters[key] = counters.get(key, 0) + len(items)
    if dry_run or table is None:
        return
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)


def main():
    parser = argparse.ArgumentParser(description="Fase B: genera y carga datos ficticios para CU-03 en DynamoDB.")
    parser.add_argument("--modo", choices=["sintetico", "transmilenio"], default="sintetico",
                         help="Estrategia de generacion (2 opciones parametrizadas requeridas por la guia).")
    parser.add_argument("--count", type=int, default=15000,
                         help="Numero de tarjetas (Cards) a generar. Minimo exigido: 15000.")
    parser.add_argument("--validations-per-card", type=int, default=3,
                         help="Numero de eventos de ValidationLog generados por cada tarjeta.")
    parser.add_argument("--ttl-days", type=int, default=400,
                         help="Dias de retencion (TTL) para ValidationLog. Debe coincidir con Terraform.")
    parser.add_argument("--profile", type=str, default=None, help="Perfil de AWS CLI (Sandbox AWS Academy).")
    parser.add_argument("--region", type=str, default="us-east-1", help="Region AWS.")
    parser.add_argument("--endpoint-url", type=str, default=None,
                         help="URL de DynamoDB Local para pruebas (ej. http://localhost:8000). Omitir para AWS real.")
    parser.add_argument("--dry-run", action="store_true",
                         help="Genera los datos y muestra el conteo sin escribir en DynamoDB.")
    parser.add_argument("--seed", type=int, default=None, help="Semilla aleatoria (reproducibilidad).")
    args = parser.parse_args()

    if args.count < 15000:
        print(f"[AVISO] --count={args.count} esta por debajo del minimo exigido (15000).")

    if args.seed is not None:
        random.seed(args.seed)

    tables = {}
    if not args.dry_run:
        session = boto3.Session(profile_name=args.profile, region_name=args.region)
        resource_kwargs = {}
        if args.endpoint_url:
            resource_kwargs["endpoint_url"] = args.endpoint_url
        dynamodb = session.resource("dynamodb", **resource_kwargs)
        tables = {
            TABLE_CARDS: dynamodb.Table(TABLE_CARDS),
            TABLE_BLACKLIST: dynamodb.Table(TABLE_BLACKLIST),
            TABLE_WHITELIST: dynamodb.Table(TABLE_WHITELIST),
            TABLE_VALIDATION_LOG: dynamodb.Table(TABLE_VALIDATION_LOG),
        }

    counters = {}
    t0 = time.time()

    cards_batch, blacklist_batch, whitelist_batch, validation_batch = [], [], [], []
    FLUSH_EVERY = 500

    for seq in range(1, args.count + 1):
        card_item, card_type, card_id = build_card(seq, args.ttl_days)
        user_id = card_item.get("userId")
        cards_batch.append(card_item)

        is_blacklisted = random.random() < 0.015  # ~1.5% de tarjetas reportadas
        if is_blacklisted:
            blacklist_batch.append(build_blacklist(card_id, user_id))

        if card_type in WHITELIST_TYPES:
            whitelist_batch.append(build_whitelist(card_id, card_type))

        validation_batch.extend(
            build_validation_logs(card_id, card_type, is_blacklisted, args.modo,
                                   args.ttl_days, args.validations_per_card)
        )

        if len(cards_batch) >= FLUSH_EVERY:
            write_batch(tables.get(TABLE_CARDS), cards_batch, args.dry_run, counters, TABLE_CARDS)
            cards_batch = []
        if len(blacklist_batch) >= FLUSH_EVERY:
            write_batch(tables.get(TABLE_BLACKLIST), blacklist_batch, args.dry_run, counters, TABLE_BLACKLIST)
            blacklist_batch = []
        if len(whitelist_batch) >= FLUSH_EVERY:
            write_batch(tables.get(TABLE_WHITELIST), whitelist_batch, args.dry_run, counters, TABLE_WHITELIST)
            whitelist_batch = []
        if len(validation_batch) >= FLUSH_EVERY:
            write_batch(tables.get(TABLE_VALIDATION_LOG), validation_batch, args.dry_run, counters, TABLE_VALIDATION_LOG)
            validation_batch = []

        if seq % 5000 == 0:
            print(f"  ... {seq}/{args.count} tarjetas procesadas")

    # flush final
    write_batch(tables.get(TABLE_CARDS), cards_batch, args.dry_run, counters, TABLE_CARDS)
    write_batch(tables.get(TABLE_BLACKLIST), blacklist_batch, args.dry_run, counters, TABLE_BLACKLIST)
    write_batch(tables.get(TABLE_WHITELIST), whitelist_batch, args.dry_run, counters, TABLE_WHITELIST)
    write_batch(tables.get(TABLE_VALIDATION_LOG), validation_batch, args.dry_run, counters, TABLE_VALIDATION_LOG)

    elapsed = time.time() - t0
    total = sum(counters.values())

    print("\n==================================================================")
    print(f" FASE B COMPLETA (modo={args.modo}, dry_run={args.dry_run})")
    print("==================================================================")
    for table_name in (TABLE_CARDS, TABLE_BLACKLIST, TABLE_WHITELIST, TABLE_VALIDATION_LOG):
        print(f"  {table_name:16s}: {counters.get(table_name, 0):,} registros")
    print(f"  {'TOTAL':16s}: {total:,} registros")
    print(f"  Tiempo: {elapsed:.1f}s")
    if total < 15000:
        print("  [AVISO] El total generado quedo por debajo de 15,000 registros.")


if __name__ == "__main__":
    main()
