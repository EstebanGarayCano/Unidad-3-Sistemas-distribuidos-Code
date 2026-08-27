# Script de verificación.

## Uso

```bash
python script3phase1.py --profile <perfil> <nombre_tabla>
```

Ejemplo:

```bash
python script3phase1.py --profile estebangaca Cards
python script3phase1.py --profile estebangaca Blacklist
python script3phase1.py --profile estebangaca Whitelist
python script3phase1.py --profile estebangaca ValidationLog
```

# Prueba Numero 1 
## python3 test/script3phase1.py --profile estebangaca Blacklist



# INFORMACIÓN DETALLADA Y APROVISIONAMIENTO: Blacklist
Estado de la Tabla         : ACTIVE
Clase de Tabla (Storage)   : STANDARD
Conteo de Ítems (Aprox.)   : 0
Tamaño de Tabla (Aprox.)   : 0.00 MB (0 bytes)

##  Esquema de Clave Primaria (Primary Key)
  • Partition Key (HASH): cardId (Tipo: S)

##  Capacidad y Aprovisionamiento de la Tabla 
Modo de Facturación / Capacidad : PAY_PER_REQUEST
  • Read Request Units Máximos  : 100
  • Write Request Units Máximos : 100

##  Warm Throughput (Pre-provisioned Instant Capacity) 
  • Read Units Regulados (Warm) : 12000
  • Write Units Regulados (Warm): 4000
  • Estado                      : ACTIVE

##  Índices Secundarios Globales (GSI) [0] 
  Ninguno registrado.

##  Índices Secundarios Locales (LSI) [0] 
  Ninguno registrado.

#  MUESTRA DE REGISTROS (MÁXIMO 5)


##  Registro #1
{
  "addedAt": "2026-05-04T21:19:02.187Z",
  "reportedBy": "CC-1074198790",
  "status": "ACTIVE",
  "verifiedBy": "FUNC-9580",
  "authorizedBy": "TM-AUTH-1363",
  "reason": "FRAUD",
  "cardId": "CARD-00008365"
}

##  Registro #2
{
  "addedAt": "2026-05-18T21:21:03.809Z",
  "verifiedBy": "FUNC-3020",
  "reportedBy": "SISTEMA-FRAUDE",
  "reason": "STOLEN",
  "cardId": "CARD-00014947",
  "status": "ACTIVE"
}

##  Registro #3
{
  "addedAt": "2026-07-08T21:16:50.257Z",
  "verifiedBy": "FUNC-1669",
  "reportedBy": "SISTEMA-FRAUDE",
  "reason": "LOST",
  "cardId": "CARD-00001410",
  "status": "ACTIVE"
}

##  Registro #4
{
  "addedAt": "2026-06-13T21:19:44.085Z",
  "verifiedBy": "FUNC-1760",
  "reportedBy": "CC-1039810570",
  "reason": "STOLEN",
  "cardId": "CARD-00010702",
  "status": "ACTIVE"
}

##  Registro #5 
{
  "addedAt": "2026-07-17T21:20:33.235Z",
  "verifiedBy": "FUNC-3280",
  "reportedBy": "SISTEMA-FRAUDE",
  "reason": "STOLEN",
  "cardId": "CARD-00013288",
  "status": "ACTIVE"
}

#  REPORTE FINAL: CONTEO DE REGISTROS (MEDIANTE SCAN)

Escaneando la tabla para obtener el número total de registros real...
Número total de registros en la tabla: 215
