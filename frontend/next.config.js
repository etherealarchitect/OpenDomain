/** @type {import('next').NextConfig} */
const apiOrigin = process.env.API_ORIGIN || process.env.NEXT_PUBLIC_API_URL;

const nextConfig = {
  output: "standalone",
  allowedDevOrigins: process.env.BASE44_PUBLIC_HOST_SUFFIX
    ? [`https://3000-${process.env.BASE44_PUBLIC_HOST_SUFFIX}`]
    : undefined,
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
