terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.60"
    }
  }
}

# region por defecto = us-east-1 para coincidir con el default del script de
# verificacion del profesor (script3phase1.py --region us-east-1 si no se especifica).
provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}
