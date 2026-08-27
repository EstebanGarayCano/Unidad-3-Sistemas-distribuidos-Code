# Fase B — Generación y carga de datos ficticios

Script: `fase_b_carga_datos.py`. Carga `Cards`, `Blacklist`, `Whitelist` y `ValidationLog` (las 4 tablas de Fase A) con datos ficticios, en proporciones que reflejan el caso de estudio:

| Tabla | % sobre las tarjetas generadas | Justificación |
|---|---|---|
| Cards | 100% (1 por tarjeta) | Cada tarjeta simulada tiene exactamente un registro |
| Blacklist | ~1.5% | El experto indicó que el fraude tecnológico no es significativo; la mayoría de bajas son por pérdida/robo, no por volumen masivo |
| Whitelist | ~12% (tipos Funcionario/Emergencia) | Coincide con los pesos de `CARD_TYPE_WEIGHTS` para esos tipos de tarjeta |
| ValidationLog | 3× por tarjeta (parametrizable) | Simula un historial reciente de validaciones por tarjeta |

## Dos opciones parametrizadas (`--modo`)

- `sintetico`: dispositivos con IDs completamente aleatorios.
- `transmilenio`: usa nombres reales de portales/troncales (fuente: [Guía General de Viaje TransMilenio](https://www.transmilenio.gov.co/files/c263614f-6156-411a-95d7-2af0b734a938/a085d5c2-2128-44c6-965f-9cf66637ef3e/Guia-General-de-viaje-de-TransMilenio-a-corte-de-diciembre-2025.pdf) y [datosabiertos-transmilenio](https://datosabiertos-transmilenio.hub.arcgis.com/)) para las validaciones en estación.

## Uso

```bash
pip install -r requirements.txt

# Prueba local sin AWS (no requiere credenciales ni tablas):
python fase_b_carga_datos.py --dry-run --count 500

# Contra DynamoDB Local (ver https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html):
python fase_b_carga_datos.py --endpoint-url http://localhost:8000 --count 1000

# Carga real en el Sandbox (después de `terraform apply` en infra/dynamodb):
python fase_b_carga_datos.py --profile sitp-sandbox --modo transmilenio --count 15000
```

`--count` es el número de tarjetas (mínimo exigido: 15000; por defecto ya viene en ese valor). Las demás tablas se derivan de esa cantidad — con el valor por defecto, el total ronda 60,000+ registros combinados.

## Verificación

Después de cargar, confirmar con el script del profesor:

```bash
python script3phase1.py --profile sitp-sandbox Cards
python script3phase1.py --profile sitp-sandbox ValidationLog
```
