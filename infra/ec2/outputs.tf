output "public_ip" {
  description = "IP publica de la instancia"
  value       = aws_instance.validation_api.public_ip
}

output "instance_id" {
  value = aws_instance.validation_api.id
}

output "ssh_command" {
  description = "Comando para conectarte (ajusta la ruta del .pem)"
  value       = "ssh -i labsuser.pem ec2-user@${aws_instance.validation_api.public_ip}"
}

output "tunnel_command" {
  description = "Comando para el tunel SSH que usara JMeter (corre desde tu Mac)"
  value       = "ssh -i labsuser.pem -L 5001:localhost:5001 ec2-user@${aws_instance.validation_api.public_ip}"
}
