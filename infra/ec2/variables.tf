variable "aws_region" {
  description = "Region AWS (Sandbox AWS Academy)"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "Perfil de AWS CLI con las credenciales del Sandbox"
  type        = string
  default     = "sitp-sandbox"
}

variable "instance_type" {
  description = "Tipo de instancia EC2. Debe estar en la lista permitida del Sandbox (t2/t3 nano-medium)."
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "Key pair para SSH. El Sandbox de AWS Academy siempre trae una llamada 'vockey'."
  type        = string
  default     = "vockey"
}

variable "my_ip_cidr" {
  description = "Tu IP publica en formato CIDR (ej. 181.56.52.254/32), para restringir el acceso SSH solo a ti."
  type        = string
}
