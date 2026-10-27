/** @type {import('next').NextConfig} */
const apiOrigin = process.env.NEXT_PUBLIC_API_URL;

// Same-origin sandbox wiring: the Next dev server proxies /api/* to the backend
// service, so browser requests (and the session cookie) stay first-party.
// Unset everywhere else, which keeps the behaviour below unchanged.
const internalApiOrigin = process.env.BACKEND_INTERNAL_URL;

// The Base44 preview serves the app through its own proxy host, so Next must
// accept that origin for dev assets and HMR. Only set in the sandbox
// (BASE44_PREVIEW_MODE=1); every other environment keeps Next's defaults.
const previewOrigin =
  process.env.BASE44_PREVIEW_MODE === "1" && process.env.BASE44_PUBLIC_HOST_SUFFIX
    ? `3000-${process.env.BASE44_PUBLIC_HOST_SUFFIX}`
    : null;

const nextConfig = {
  output: "standalone",
  allowedDevOrigins: previewOrigin ? [previewOrigin] : undefined,
  async rewrites() {
    // In production Caddy sends /api directly to FastAPI. Only use a Next.js
    // rewrite for local development with an explicit backend origin.
    const destination =
      internalApiOrigin || (apiOrigin && !apiOrigin.startsWith("/") ? apiOrigin : null);

    if (!destination) {
      return [];
    }

    return [
      {
        source: "/api/:path*",
        destination: `${destination}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
