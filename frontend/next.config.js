/** @type {import('next').NextConfig} */
const apiOrigin = process.env.NEXT_PUBLIC_API_URL;
// Optional same-origin development proxy, e.g. http://backend:8000 in Docker.
// Keeps browser API calls on the page's own origin so the HttpOnly session
// cookie stays first-party.
const apiProxyTarget = process.env.API_PROXY_TARGET;
const previewHostSuffix = process.env.BASE44_PUBLIC_HOST_SUFFIX;

const nextConfig = {
  output: "standalone",
  // Allow the sandbox preview origin to load dev assets and HMR. Wildcards only
  // cover subdomains, so the preview hostname is listed explicitly.
  ...(process.env.BASE44_PREVIEW_MODE === "1" && previewHostSuffix
    ? { allowedDevOrigins: [`3000-${previewHostSuffix}`] }
    : {}),
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
