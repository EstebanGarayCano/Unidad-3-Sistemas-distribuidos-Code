variable "aws_region" {
  description = "Region AWS donde se despliegan las tablas (Sandbox AWS Academy)"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "Perfil de AWS CLI configurado con las credenciales temporales del Sandbox (AWS Academy Learner Lab). Debe coincidir con el <NOMBRE_DEL_PROFILE> compartido con el profesor."
  type        = string
  default     = "sitp-sandbox"
}

variable "max_read_request_units" {
  description = "Tope de Read Request Units por tabla en modo On-Demand. Protege el presupuesto de USD 20 del Sandbox (ver justificacion en la seccion 4.3 del documento)."
  type        = number
  default     = 100
}

variable "max_write_request_units" {
  description = "Tope de Write Request Units por tabla en modo On-Demand. Protege el presupuesto de USD 20 del Sandbox (ver justificacion en la seccion 4.3 del documento)."
  type        = number
  default     = 100
}

variable "validation_log_ttl_days" {
  description = "Dias de retencion de los registros de ValidationLog antes de expirar via TTL"
  type        = number
  default     = 400
}

variable "tags" {
  description = "Tags comunes aplicados a las 4 tablas"
  type        = map(string)
  default = {
    Project     = "SITP-Validacion-Tarjetas"
    Course      = "Unidad3-SistemasDistribuidos"
    ManagedBy   = "Terraform"
    Environment = "sandbox"
  }
}
