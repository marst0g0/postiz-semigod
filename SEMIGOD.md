# Fork SemiGod de Postiz

Fork mínimo de [gitroomhq/postiz-app](https://github.com/gitroomhq/postiz-app).
Todo el cambio vive en commits cuyo mensaje empieza con `[semigod-patch]`
(hoy uno solo, ~40 líneas). Este archivo y el workflow no se aplican a la imagen.

## Qué cambia

| Variable | Dónde | Para qué | Si no se define |
| --- | --- | --- | --- |
| `CLOUDFLARE_ENDPOINT` | `.env` del servidor | Endpoint S3 de otro proveedor, ej. `https://ny-s3.storage.bunnycdn.com` | R2 (igual que upstream) |
| `CLOUDFLARE_FORCE_PATH_STYLE` | `.env` del servidor | `true` si el proveedor quiere URLs `/bucket/key` | `false` |
| `MAX_VIDEO_UPLOAD_MB` | `.env` del servidor | Tope de video en el backend | 1024 |
| `NEXT_PUBLIC_MAX_VIDEO_UPLOAD_MB` | build arg (workflow) | Tope de video en el frontend | 1024 |
| `OPENAI_MODEL` | `.env` del servidor | Modelo de texto para TODAS las funciones de IA (chat, mejora de posts, agente, extracción). Ej. `openai/gpt-4.1` en OpenRouter | Los de upstream (`gpt-4.1`, `gpt-5.2`, `gpt-4o-2024-08-06`) |
| `OPENAI_IMAGE_MODEL` | `.env` del servidor | Modelo de imágenes | `chatgpt-image-latest` |
| `OPENAI_BASE_URL` | `.env` del servidor | Lo leen los SDK de OpenAI; ej. `https://openrouter.ai/api/v1`. Con esto el agente usa Chat Completions | `https://api.openai.com/v1` |

Se sigue usando `STORAGE_PROVIDER=cloudflare` y el resto de variables `CLOUDFLARE_*`.

## Actualizar a un release nuevo

El workflow **SemiGod build** corre cada lunes: si salió un release nuevo,
aplica el parche encima y publica `ghcr.io/<dueño>/postiz-semigod:<tag>-semigod`.
También se puede correr a mano desde Actions indicando el tag.

Si falla con "El parche no aplica":

```bash
git fetch upstream --tags
git checkout -b fix vX.Y.Z
git cherry-pick <commit [semigod-patch]>   # resolver conflictos
# actualizar el commit [semigod-patch] en la rama semigod/patches con la versión resuelta
```

## Proponer upstream

Si Postiz acepta un endpoint S3 configurable y un tope de video configurable,
este fork deja de ser necesario: volver a la imagen oficial.

## Despliegue y operación (ergon_2)

Los archivos de operación (compose, Nginx interno, páginas legales, backup, recordatorios y firewall) están en
[`deploy/ergon_2/`](deploy/ergon_2/README.md), sin secretos. Notas aprendidas en la puesta en marcha:

- El Nginx interno de Postiz espera por defecto 60 s la respuesta del backend; las subidas grandes (800 MB+) daban 504.
  Se corrige con `proxy_read_timeout`/`proxy_send_timeout` en `deploy/ergon_2/nginx.conf`.
- Instagram Standalone usa `INSTAGRAM_APP_ID/SECRET` y el callback `/integrations/social/instagram-standalone`; Facebook usa
  `FACEBOOK_APP_ID/SECRET` y `/integrations/social/facebook`. Facebook solo publica en páginas, no en perfiles personales.
- El log `[semigod] NotEnoughScopes` (parche `[semigod-patch]`) indica qué scopes faltan; `concedidos []` significa que falló
  el intercambio del código por el token (secret o redirect URI incorrectos), no un problema de scopes.
- Con `DISABLE_REGISTRATION=true` una invitación no permite crear la cuenta: hay que abrir el registro temporalmente.
