/** @type {import('next').NextConfig} */
const apiOrigin = process.env.NEXT_PUBLIC_API_URL;

// Sandbox preview overrides, active only when BASE44_PREVIEW_MODE === "1".
//
// The preview serves the app from a single origin (host port 3000) and the session
// cookie is SameSite=Lax, so browser requests must not go cross-origin to the API.
// With API_PROXY_TARGET set, the dev server proxies /api/* to the backend service
// instead. Without the flag (or the variable) behaviour below is unchanged:
// rewrites stay empty unless NEXT_PUBLIC_API_URL is an explicit backend origin.
const sandboxPreview = process.env.BASE44_PREVIEW_MODE === "1";
const apiProxyTarget = sandboxPreview ? process.env.API_PROXY_TARGET : undefined;
const previewOrigin = process.env.BASE44_PUBLIC_HOST_SUFFIX
  ? `3000-${process.env.BASE44_PUBLIC_HOST_SUFFIX}`
  : undefined;

const nextConfig = {
  output: "standalone",
  // The preview reaches the dev server through the proxy, so its origin must be
  // allow-listed or Next.js blocks dev assets and HMR.
  allowedDevOrigins:
    sandboxPreview && previewOrigin ? [previewOrigin] : [],
  async rewrites() {
    if (apiProxyTarget) {
      return [
        {
          source: "/api/:path*",
          destination: `${apiProxyTarget}/api/:path*`,
        },
      ];
    }

    // In production Caddy sends /api directly to FastAPI. Only use a Next.js
    // rewrite for local development with an explicit backend origin.
    if (!apiOrigin || apiOrigin.startsWith("/")) {
      return [];
    }

    return [
      {
        source: "/api/:path*",
        destination: `${apiOrigin}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
