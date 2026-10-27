/** @type {import('next').NextConfig} */
const apiOrigin = process.env.NEXT_PUBLIC_API_URL;

// Base44 sandbox preview only (BASE44_PREVIEW_MODE=1). The preview is served
// from port 3000 on a public host, so the app runs single-origin: this rewrite
// proxies /api/* from the browser to the backend service on the compose
// network, which keeps session cookies first-party. Unset (production, or a
// developer running Next directly) none of this applies.
const previewApiTarget =
  process.env.BASE44_PREVIEW_MODE === "1" ? process.env.API_PROXY_TARGET : undefined;

// Next >= 15.5 rejects dev asset/HMR requests whose Origin is not listed here.
// The browser's Origin is the public preview host, e.g. "3000-<suffix>".
const allowedDevOrigins =
  process.env.BASE44_PREVIEW_MODE === "1" && process.env.BASE44_PUBLIC_HOST_SUFFIX
    ? [`3000-${process.env.BASE44_PUBLIC_HOST_SUFFIX}`]
    : [];

const nextConfig = {
  output: "standalone",
  ...(allowedDevOrigins.length ? { allowedDevOrigins } : {}),
  async rewrites() {
    if (previewApiTarget) {
      return [
        {
          source: "/api/:path*",
          destination: `${previewApiTarget}/api/:path*`,
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
