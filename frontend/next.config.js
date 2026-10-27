/** @type {import('next').NextConfig} */
// Server-side proxy target for the same-origin /api rewrite. Production routes
// /api through Caddy, so this is only set when the browser must keep talking to
// Next on the same origin while FastAPI runs behind it (Base44 sandbox, and any
// local run that needs first-party session cookies).
const apiOrigin = process.env.NEXT_PUBLIC_API_URL || process.env.API_PROXY_TARGET;
// The sandbox serves the app through a proxied preview origin. The dev server
// only accepts it when explicitly allowed, gated on BASE44_PREVIEW_MODE being
// exactly "1"; both variables are supplied by docker-compose.base44.yml.
const previewHostSuffix = process.env.BASE44_PUBLIC_HOST_SUFFIX;
const sandboxDevOrigins =
  process.env.BASE44_PREVIEW_MODE === "1" && previewHostSuffix
    ? [`3000-${previewHostSuffix}`]
    : [];

const nextConfig = {
  output: "standalone",
  ...(sandboxDevOrigins.length > 0 ? { allowedDevOrigins: sandboxDevOrigins } : {}),
  async rewrites() {
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
