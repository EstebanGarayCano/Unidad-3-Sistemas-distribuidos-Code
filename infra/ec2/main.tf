# Fase C - EC2 minimo para alojar el API de medicion de performance (CU-03).
#
# Usa la VPC y el AMI de Amazon Linux por defecto de la cuenta (el Sandbox
# solo permite AMIs provistas por Amazon). El acceso es unicamente por SSH

data "aws_vpc" "default" {
  default = true
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_security_group" "validation_api" {
  name        = "sitp-validation-api-ssh"
  description = "Solo SSH desde mi IP. Sin puertos abiertos al publico."
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH solo desde mi IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip_cidr]
  }

  egress {
    description = "Salida libre (para instalar Docker, git clone, etc.)"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Project   = "SITP-Validacion-Tarjetas"
    Course    = "Unidad3-SistemasDistribuidos"
    ManagedBy = "Terraform"
  }
}

resource "aws_instance" "validation_api" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  key_name      = var.key_name
  # No se asigna iam_instance_profile: el rol IAM esta en solo lectura en el
  # Sandbox y bloquea tambien iam:PassRole (verificado con un intento real de
  # apply -- UnauthorizedOperation: ... is not authorized to perform:
  # iam:PassRole). No importa que EMR_EC2_DefaultRole ya exista y tenga
  # dynamodb:*: no podemos "asignarselo" a la instancia al lanzarla. En su
  # lugar, la app recibe las credenciales temporales de la sesion como
  # variables de entorno al correr el contenedor Docker (ver services/
  # ValidationApi/README.md).
  vpc_security_group_ids = [aws_security_group.validation_api.id]

  root_block_device {
    volume_size = 30 # AMI base requiere >=30GB; limite del Sandbox es 35GB
    volume_type = "gp2"
  }

  tags = {
    Name      = "sitp-validation-api"
    Project   = "SITP-Validacion-Tarjetas"
    Course    = "Unidad3-SistemasDistribuidos"
    ManagedBy = "Terraform"
    TableRole = "Fase C - host del API de medicion CU-03"
  }
}
