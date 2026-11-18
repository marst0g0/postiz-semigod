// SemiGod fork: lets the "cloudflare" storage provider talk to any
// S3-compatible store (Bunny Storage, MinIO, AWS S3...) and raises the
// video size cap. Every value falls back to upstream behaviour when unset.

// CLOUDFLARE_ENDPOINT, e.g. https://ny-s3.storage.bunnycdn.com
export function s3Endpoint(accountId?: string): string {
  return (
    process.env.CLOUDFLARE_ENDPOINT ||
    `https://${accountId}.r2.cloudflarestorage.com`
  );
}

// CLOUDFLARE_FORCE_PATH_STYLE=true for stores that want /bucket/key URLs
export function s3ForcePathStyle(): boolean {
  return process.env.CLOUDFLARE_FORCE_PATH_STYLE === 'true';
}

// MAX_VIDEO_UPLOAD_MB, upstream default 1024 (1 GB)
export function maxVideoUploadBytes(): number {
  const mb = Number(process.env.MAX_VIDEO_UPLOAD_MB);
  return (Number.isFinite(mb) && mb > 0 ? mb : 1024) * 1024 * 1024;
}
