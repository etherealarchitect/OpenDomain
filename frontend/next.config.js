/** @type {import('next').NextConfig} */
// Server-only backend origin used by the dev-server rewrite proxy. Kept separate
// from NEXT_PUBLIC_API_URL so the browser always calls same-origin /api (cookie
// auth stays single-origin) while the Next server proxies to FastAPI internally.
const backendOrigin =
  process.env.BACKEND_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL;

const allowedDevOrigins = process.env.BASE44_PUBLIC_HOST_SUFFIX
  ? [`https://3000-${process.env.BASE44_PUBLIC_HOST_SUFFIX}`]
  : [];

const nextConfig = {
  output: "standalone",
  allowedDevOrigins,
  async rewrites() {
    // In production Caddy sends /api directly to FastAPI. Only use a Next.js
    // rewrite for local development with an explicit backend origin.
    if (!backendOrigin || backendOrigin.startsWith("/")) {
      return [];
    }

    return [
      {
        source: "/api/:path*",
        destination: `${backendOrigin}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
