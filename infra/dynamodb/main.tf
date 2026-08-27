# Fase A - Configuracion de DynamoDB (Sandbox AWS Academy)
#
# Se despliegan unicamente las 4 tablas que soportan CU-03 (Validacion de
# usuario final), segun lo acordado: el modelamiento UML/API cubre los 3
# casos de uso, pero solo CU-03 se implementa fisicamente en el Sandbox.
#
# Billing mode On-Demand con tope explicito de RRU/WRU (var.max_read_request_units
# / var.max_write_request_units): evita calcular RCU/WCU a mano y acota el gasto
# maximo posible, clave dado el limite de USD 20 del Sandbox (ver seccion 4.3).
#
# Cifrado en reposo: se deja el default de DynamoDB (AWS owned key, sin costo).
# No se declara el bloque server_side_encryption a proposito -- declararlo con
# enabled = true activaria la KMS administrada por AWS, que si tiene costo.
#
# Nota: `terraform validate` marca hash_key/range_key como deprecados en favor
# de "key_schema". Se verifico con `terraform providers schema -json` (provider
# hashicorp/aws 6.62.0) y ese atributo aun no existe en el schema -- es un aviso
# adelantado sin reemplazo funcional todavia, por lo que se mantiene hash_key/
# range_key intencionalmente.

resource "aws_dynamodb_table" "cards" {
  name         = "Cards"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "cardId"

  attribute {
    name = "cardId"
    type = "S"
  }

  attribute {
    name = "userId"
    type = "S"
  }

  # GSI administrativo: soporta la regla "maximo una tarjeta activa por tipo
  # por persona" (CU-01/CU-02). No se usa en el camino critico de validacion.
  global_secondary_index {
    name            = "userId-index"
    hash_key        = "userId"
    projection_type = "ALL"
  }

  on_demand_throughput {
    max_read_request_units  = var.max_read_request_units
    max_write_request_units = var.max_write_request_units
  }

  tags = merge(var.tags, {
    TableRole = "Estado de tarjeta - saldo tipo y parametros de consumo"
  })
}

resource "aws_dynamodb_table" "blacklist" {
  name         = "Blacklist"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "cardId"

  attribute {
    name = "cardId"
    type = "S"
  }

  # Streams habilitado: alimenta el log de auditoria append-only
  # (tactica de Seguridad del arbol de utilidad).
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  on_demand_throughput {
    max_read_request_units  = var.max_read_request_units
    max_write_request_units = var.max_write_request_units
  }

  tags = merge(var.tags, {
    TableRole = "Lista negra CU-02"
  })
}

resource "aws_dynamodb_table" "whitelist" {
  name         = "Whitelist"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "cardId"

  attribute {
    name = "cardId"
    type = "S"
  }

  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  on_demand_throughput {
    max_read_request_units  = var.max_read_request_units
    max_write_request_units = var.max_write_request_units
  }

  tags = merge(var.tags, {
    TableRole = "Lista blanca CU-01"
  })
}

resource "aws_dynamodb_table" "validation_log" {
  name         = "ValidationLog"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "cardId"
  range_key    = "timestamp"

  attribute {
    name = "cardId"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  # TTL: controla el crecimiento de la tabla de mayor volumen de escritura
  # (un registro por validacion). El script de carga (Fase B) debe poblar el
  # atributo "ttl" (epoch seconds) en cada item.
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  on_demand_throughput {
    max_read_request_units  = var.max_read_request_units
    max_write_request_units = var.max_write_request_units
  }

  tags = merge(var.tags, {
    TableRole = "Historico de validaciones CU-03"
  })
}
