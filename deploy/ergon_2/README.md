# Despliegue en ergon_2 (Postiz SemiGod)

Copia de los archivos de operación de `/opt/postiz` en ergon_2. **No contiene secretos**: el `.env` real,
`.apikey` y `backup/.passphrase` no se versionan (`.env.example` solo trae los nombres de las variables).

| Archivo | Va en | Para qué |
| --- | --- | --- |
| `docker-compose.yaml` | `/opt/postiz/` | Stack de 6 contenedores; monta `legal/` y `nginx.conf` |
| `nginx.conf` | `/opt/postiz/` | Nginx interno de Postiz con `/legal/`, endpoints de Meta y timeouts de 3600 s para subidas grandes |
| `legal/` | `/opt/postiz/legal/` | Página principal, privacidad, términos y eliminación de datos (URLs públicas `/legal/...`) |
| `backup/backup.sh` | `/opt/postiz/backup/` | Backup diario cifrado a Google Drive (cron 03:30) |
| `reminders/token_reminder.py` | `/opt/postiz/reminders/` | Aviso por correo a 10 y 3 días del vencimiento de tokens (cron 09:15) |
| `firewall/` | `/usr/local/sbin/` y `/etc/systemd/system/` | Restringe el puerto 4007 al proxy 10.0.0.90 en cada arranque |

Si se actualiza la imagen de Postiz y cambia su Nginx interno, hay que rehacer `nginx.conf` a partir del nuevo.
