/** @type {import('next').NextConfig} */
const apiOrigin = process.env.NEXT_PUBLIC_API_URL;

const nextConfig = {
  output: "standalone",
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
