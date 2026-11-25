#!/usr/bin/env bash
# Backup cifrado de Postiz -> Google Drive (rclone remoto Inventario-Backup:, carpeta Postiz-Backup)
set -euo pipefail
BASE=/opt/postiz
DEST="Inventario-Backup:Postiz-Backup"
KEEP_REMOTE_DAYS=30
KEEP_LOCAL=3
TS=$(date +%Y%m%d-%H%M%S)
WORK=$BASE/backup/tmp/$TS
OUT=$BASE/backup/local
export PATH="$PATH:/home/dev/.local/bin"
mkdir -p "$WORK" "$OUT"; chmod 700 "$WORK" "$OUT"
trap 'rm -rf "$WORK"' EXIT
log(){ echo "$(date '+%F %T') $*"; }

log "dump postiz"
docker exec postiz-postgres pg_dump -U postiz -Fc postiz > "$WORK/postiz.dump"
log "dump temporal"
docker exec temporal-postgresql pg_dump -U temporal -Fc temporal > "$WORK/temporal.dump"
log "config"
tar -C "$BASE" -czf "$WORK/config.tar.gz" .env docker-compose.yaml nginx.conf dynamicconfig legal
# sanity: los dumps no pueden estar vacíos
for f in postiz.dump temporal.dump config.tar.gz; do [ -s "$WORK/$f" ] || { log "ERROR $f vacío"; exit 1; }; done
pg_restore -l "$WORK/postiz.dump" >/dev/null 2>&1 || docker exec -i postiz-postgres pg_restore -l < "$WORK/postiz.dump" >/dev/null

ARCH="$OUT/postiz-$TS.tar.gz.gpg"
tar -C "$WORK" -cf - postiz.dump temporal.dump config.tar.gz | gzip -1 \
  | gpg --batch --yes --symmetric --cipher-algo AES256 --passphrase-file "$BASE/backup/.passphrase" -o "$ARCH"
log "cifrado: $(du -h "$ARCH" | cut -f1)"

rclone copy "$ARCH" "$DEST" --drive-chunk-size 8M
rclone lsf "$DEST" | grep -q "$(basename "$ARCH")" || { log "ERROR no aparece en Drive"; exit 1; }
log "subido a $DEST"

rclone delete "$DEST" --min-age ${KEEP_REMOTE_DAYS}d
ls -1t "$OUT"/postiz-*.gpg 2>/dev/null | tail -n +$((KEEP_LOCAL+1)) | xargs -r rm -f
log "OK"
