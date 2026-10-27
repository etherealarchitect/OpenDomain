/** @type {import('next').NextConfig} */
const apiOrigin = process.env.NEXT_PUBLIC_API_URL;
// Optional same-origin development proxy target (for example http://backend:8000
// inside the sandbox stack). Server-side only: the browser keeps calling
// same-origin /api/v1, so the HttpOnly session cookie stays first-party.
const apiProxyTarget = process.env.API_PROXY_TARGET;
// Next.js gates dev assets and HMR by origin. The sandbox preview origin is
// derived from BASE44_PUBLIC_HOST_SUFFIX and allowed only in preview mode.
const allowedDevOrigins =
  process.env.BASE44_PREVIEW_MODE === "1" && process.env.BASE44_PUBLIC_HOST_SUFFIX
    ? [`3000-${process.env.BASE44_PUBLIC_HOST_SUFFIX}`]
    : [];

const nextConfig = {
  output: "standalone",
  allowedDevOrigins,
  async rewrites() {
    const proxyTarget = apiProxyTarget || apiOrigin;
    // In production Caddy sends /api directly to FastAPI. Only use a Next.js
    // rewrite for local development with an explicit backend origin.
    if (!proxyTarget || proxyTarget.startsWith("/")) {
      return [];
    }

    return [
      {
        source: "/api/:path*",
        destination: `${proxyTarget}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
