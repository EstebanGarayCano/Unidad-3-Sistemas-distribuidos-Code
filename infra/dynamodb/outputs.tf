output "table_names" {
  description = "Nombres de las 4 tablas desplegadas. Usar con: python script3phase1.py --profile <perfil> <nombre_tabla>"
  value = {
    cards          = aws_dynamodb_table.cards.name
    blacklist      = aws_dynamodb_table.blacklist.name
    whitelist      = aws_dynamodb_table.whitelist.name
    validation_log = aws_dynamodb_table.validation_log.name
  }
}

output "table_arns" {
  description = "ARNs de las 4 tablas, para configurar politicas IAM de los microservicios"
  value = {
    cards          = aws_dynamodb_table.cards.arn
    blacklist      = aws_dynamodb_table.blacklist.arn
    whitelist      = aws_dynamodb_table.whitelist.arn
    validation_log = aws_dynamodb_table.validation_log.arn
  }
}

output "blacklist_stream_arn" {
  description = "ARN del stream de Blacklist (para el consumidor de auditoria)"
  value       = aws_dynamodb_table.blacklist.stream_arn
}

output "whitelist_stream_arn" {
  description = "ARN del stream de Whitelist (para el consumidor de auditoria)"
  value       = aws_dynamodb_table.whitelist.stream_arn
}
