# ValidationApi — arnés de medición Fase C

API mínimo en ASP.NET Core (.NET 10) con dos endpoints que ejercitan directamente DynamoDB, usados para la prueba de performance de CU-03 con JMeter. **No** es la implementación completa del microservicio de validación (esa cubriría lista negra, saldo, anti-passback y lista blanca en una sola transacción, según el diseño de la sección 3.3 del documento) — aquí se aíslan a propósito las dos operaciones que la actividad pide medir.

| Endpoint | Operación DynamoDB | Tabla |
|---|---|---|
| `GET /cards/{cardId}` | `GetItem` (lectura) | `Cards` |
| `POST /validations` | `PutItem` (escritura) | `ValidationLog` |

## Correr local (requiere credenciales AWS configuradas)

```bash
dotnet run
```

## Construir y correr con Docker (en la EC2)

```bash
docker build -t validation-api .
docker run -d -p 5001:8080 --name validation-api validation-api
```

La imagen usa el rol IAM de la instancia (`EMR_EC2_DefaultRole`) para autenticarse contra DynamoDB — no necesita credenciales explícitas dentro del contenedor.
