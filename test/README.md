# Script de verificación del profesor

`script3phase1.py` es una copia del script oficial de verificación de la Actividad 3, publicado por el profesor Francisco Javier Moreno Díaz en [fmorenod81/unisabana](https://github.com/fmorenod81/unisabana/tree/main/posgraduate/swarch/script_3). Se guarda aquí únicamente para probar localmente que funciona correctamente contra las credenciales del Sandbox **antes** de enviárselas al profesor, tal como él mismo lo recomienda.

No es código propio de este proyecto — no modificar. Cualquier actualización se trae de nuevo desde el repositorio original.

## Uso

```bash
python script3phase1.py --profile <perfil> <nombre_tabla>
```

Ejemplo:

```bash
python script3phase1.py --profile estebangaca Cards
python script3phase1.py --profile estebangaca Blacklist
python script3phase1.py --profile estebangaca Whitelist
python script3phase1.py --profile estebangaca ValidationLog
```
