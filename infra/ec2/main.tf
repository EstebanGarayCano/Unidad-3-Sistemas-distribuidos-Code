# Fase C - EC2 minimo para alojar el API de medicion de performance (CU-03).
#
# Usa la VPC y el AMI de Amazon Linux por defecto de la cuenta (el Sandbox
# solo permite AMIs provistas por Amazon). El acceso es unicamente por SSH
# desde tu IP -- el puerto de la aplicacion (5001) nunca se abre al publico,
# se llega a el mediante un tunel SSH desde tu maquina.

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
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  key_name               = var.key_name
  iam_instance_profile   = var.instance_profile_name
  vpc_security_group_ids = [aws_security_group.validation_api.id]

  root_block_device {
    volume_size = 20 # dentro del limite de 35 GB del Sandbox
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
