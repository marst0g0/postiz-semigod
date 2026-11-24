/**
 * [semigod-patch] Modelos de IA configurables por variable de entorno.
 *
 * - OPENAI_MODEL        : si está definida, reemplaza TODOS los modelos de texto
 *                         (chat, mejora de posts, agente, extracción).
 * - OPENAI_IMAGE_MODEL  : reemplaza el modelo de imágenes.
 * - OPENAI_BASE_URL     : (la leen los SDK) permite apuntar a OpenRouter u otro
 *                         endpoint compatible, p. ej. https://openrouter.ai/api/v1
 *
 * Sin variables, el comportamiento es idéntico al de upstream.
 */
export const textModel = (upstreamDefault: string): string =>
  process.env.OPENAI_MODEL?.trim() || upstreamDefault;

export const imageModel = (upstreamDefault: string): string =>
  process.env.OPENAI_IMAGE_MODEL?.trim() || upstreamDefault;

export const hasCustomOpenAIBaseUrl = (): boolean =>
  !!process.env.OPENAI_BASE_URL?.trim();
