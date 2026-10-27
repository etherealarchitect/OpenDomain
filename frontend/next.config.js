/** @type {import('next').NextConfig} */
const apiOrigin = process.env.NEXT_PUBLIC_API_URL;

// Sandbox preview overrides, active only when BASE44_PREVIEW_MODE === "1".
//
// The preview serves everything from a single origin (host port 3000) and the
// backend session cookie is SameSite=Lax, so the browser must not call the API
// cross-origin: with API_PROXY_TARGET set, the dev server proxies /api/* to the
// backend service instead. The preview also arrives through a proxy, so its
// origin has to be allow-listed or Next.js blocks dev assets and HMR.
// With the flag unset (or any other value) behaviour below is unchanged:
// rewrites stay empty unless NEXT_PUBLIC_API_URL is an explicit backend origin.
const sandboxPreview = process.env.BASE44_PREVIEW_MODE === "1";
const apiProxyTarget = sandboxPreview ? process.env.API_PROXY_TARGET : undefined;
const previewOrigin = process.env.BASE44_PUBLIC_HOST_SUFFIX
  ? `3000-${process.env.BASE44_PUBLIC_HOST_SUFFIX}`
  : undefined;

const nextConfig = {
  output: "standalone",
  allowedDevOrigins: sandboxPreview && previewOrigin ? [previewOrigin] : [],
  // Several API paths end in a slash (`/whois/`, `/contacts/`, `/domains/`,
  // `/domains/{id}/dns/`, `/webhooks/`, `/api-keys/`). Redirecting them strips
  // the slash, and FastAPI then answers 307 to an absolute internal URL
  // (`http://backend:8000/...`) that the browser cannot resolve. Production
  // never hits this: Caddy passes /api straight through. Off unless the
  // sandbox flag is set, where `false` is the framework default anyway.
  skipTrailingSlashRedirect: sandboxPreview,
  async rewrites() {
    if (apiProxyTarget) {
      return [
        // Trailing-slash API paths (`/whois/`, `/contacts/`, `/domains/`,
        // `/domains/{id}/dns/`, `/webhooks/`, `/api-keys/`): keep the slash so
        // FastAPI matches its own route instead of answering 307 to an
        // absolute internal URL the browser cannot resolve.
        {
          source: "/api/:path*/",
          destination: `${apiProxyTarget}/api/:path*/`,
        },
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
