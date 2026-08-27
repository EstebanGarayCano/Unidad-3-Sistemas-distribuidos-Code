# Fase A — DynamoDB (Sandbox AWS Academy)

Despliega las 4 tablas que soportan CU-03 (Validación de usuario final): `Cards`, `Blacklist`, `Whitelist`, `ValidationLog`. Ver diseño completo en la sección 4 del documento (repo `Unidad-3-Sistemas-distribuidos`).

## Prerrequisitos

1. Sesión activa del AWS Academy Learner Lab (botón "Start Lab").
2. Copiar las credenciales temporales (Access Key, Secret Key, Session Token) a un perfil local:

```bash
aws configure set aws_access_key_id     <ACCESS_KEY>     --profile sitp-sandbox
aws configure set aws_secret_access_key <SECRET_KEY>     --profile sitp-sandbox
aws configure set aws_session_token     <SESSION_TOKEN>  --profile sitp-sandbox
aws configure set region                us-east-1        --profile sitp-sandbox
```

3. Verificar acceso: `aws sts get-caller-identity --profile sitp-sandbox`

## Uso

```bash
cd infra/dynamodb
cp terraform.tfvars.example terraform.tfvars   # ajustar si el perfil tiene otro nombre
terraform init
terraform plan
terraform apply
```

Al terminar, `terraform output table_names` lista los nombres exactos a usar con el script de verificación del profesor:

```bash
python script3phase1.py --profile sitp-sandbox Cards
python script3phase1.py --profile sitp-sandbox Blacklist
python script3phase1.py --profile sitp-sandbox Whitelist
python script3phase1.py --profile sitp-sandbox ValidationLog
```

## Para destruir (liberar presupuesto al terminar la ventana de revisión)

```bash
terraform destroy
```
