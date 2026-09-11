import type { Metadata } from "next";
import { Lato, Open_Sans, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";
import { Sidebar } from "@/components/layout/sidebar";
import { TopBar } from "@/components/layout/top-bar";

// Base44 Typography Configuration
const lato = Lato({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-heading",
  weight: ["300", "400", "500", "600", "700", "900"],
  fallback: ["ui-sans-serif", "system-ui", "sans-serif"],
});

const openSans = Open_Sans({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-body",
  weight: ["300", "400", "500", "600", "700", "800"],
  fallback: ["ui-sans-serif", "system-ui", "sans-serif"],
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-mono",
  fallback: ["ui-monospace", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "monospace"],
});

export const metadata: Metadata = {
  title: {
    default: "OpenDomain · AI-Powered Domain Management",
    template: "%s · OpenDomain",
  },
  description: "Open-source domain registrar platform with integrated AI agent. Manage your entire domain fleet — search, register, configure DNS, monitor uptime, and trade on the marketplace — all from a single agentic terminal powered by Claude.",
  keywords: ["domain", "registrar", "DNS", "AI agent", "Claude", "open source", "domain management"],
  authors: [{ name: "OpenDomain Team" }],
  creator: "OpenDomain",
  publisher: "OpenDomain",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://opendomain.etherealcode.org",
    title: "OpenDomain · AI-Powered Domain Management",
    description: "Open-source domain registrar platform with integrated AI agent.",
    siteName: "OpenDomain",
    images: [
      {
        url: "https://opendomain.etherealcode.org/og-image.png",
        width: 1200,
        height: 630,
        alt: "OpenDomain AI-Powered Domain Management",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "OpenDomain · AI-Powered Domain Management",
    description: "Open-source domain registrar platform with integrated AI agent.",
    images: ["https://opendomain.etherealcode.org/og-image.png"],
    creator: "@opendomain",
  },
  icons: {
    icon: [
      {
        url: "/favicon.svg",
        type: "image/svg+xml",
      },
      {
        url: "/favicon-32x32.png",
        sizes: "32x32",
        type: "image/png",
      },
      {
        url: "/favicon-16x16.png",
        sizes: "16x16",
        type: "image/png",
      },
    ],
    apple: [
      {
        url: "/apple-touch-icon.png",
        sizes: "180x180",
        type: "image/png",
      },
    ],
  },
  manifest: "/site.webmanifest",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${lato.variable} ${openSans.variable} ${jetbrainsMono.variable}`} suppressHydrationWarning>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
        <meta name="theme-color" content="#8a5bd1" />
        {/* Base44 Design System Font Configuration */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="min-h-screen bg-gradient-to-br from-background via-background to-background/95 font-body text-foreground antialiased leading-relaxed">
        {/* Base44 Background Effects */}
        <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
          {/* Base44 Gradient 1 - effects.gradients[0] */}
          <div className="absolute -top-40 -right-40 h-80 w-80 bg-gradient-to-br from-primary/20 via-primary/10 to-accent/20 rounded-full blur-3xl opacity-30 animate-pulse" />
          {/* Base44 Gradient 2 - effects.gradients[1] */}
          <div className="absolute -bottom-40 -left-40 h-80 w-80 bg-gradient-to-br from-accent/20 via-primary/10 to-primary/20 rounded-full blur-3xl opacity-30 animate-pulse delay-1000" />
          {/* Base44 Gradient 5 - effects.gradients[4] */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[500px] w-[500px] bg-gradient-radial from-primary/10 via-transparent to-transparent blur-3xl opacity-20" />
          {/* Base44 Gradient 6 - effects.gradients[5] */}
          <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-accent/5 via-transparent to-primary/5 opacity-50" />
          {/* Base44 Glow Shadow Effects - effects.shadows.glow */}
          <div className="absolute inset-0 -inset-2 bg-gradient-to-r from-primary/20 to-accent/20 blur-xl opacity-20 pointer-events-none" />
          {/* Base44 Shimmer Effect - effects.animations.shimmer */}
          <div className="absolute inset-0 animate-shimmer bg-gradient-to-r from-transparent via-primary/5 to-transparent opacity-30" />
        </div>

        <Providers>
          {/* Base44 Grid Layout System */}
          <div className="flex h-screen">
            {/* Sidebar will use Base44 sidebar styling */}
            <Sidebar />
            <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
              {/* TopBar will use Base44 topbar styling */}
              <TopBar />
              {/* Main Content with Base44 Container Patterns */}
              <main className="flex-1 overflow-auto bg-gradient-to-br from-background/40 via-background/30 to-background/20 backdrop-blur-sm">
                {/* Base44 Container - max-w-7xl from layout.gridSystem.container */}
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 container-base44-large">
                  {/* Base44 Glass Card with Terminal Effect */}
                  <div className="card-base44-terminal shadow-base44-lg relative overflow-hidden">
                    {/* Base44 Terminal Header Effect */}
                    <div className="card-base44-header shadow-base44">
                      <div className="flex items-center gap-2">
                        <div className="flex gap-1">
                          <div className="terminal-base44-dot bg-destructive" />
                          <div className="terminal-base44-dot bg-warning" />
                          <div className="terminal-base44-dot bg-success" />
                        </div>
                        <span className="text-xs font-medium text-foreground/80 font-mono">opendomain:~$</span>
                      </div>
                    </div>

                    {/* Base44 Flexible Grid System - layout.gridSystem.flexible */}
                    <div className="flex flex-wrap gap-4 sm:gap-6 lg:gap-8 mt-8">
                      {children}
                    </div>

                    {/* Base44 Terminal Bottom Elements */}
                    <div className="mt-8 pt-6 border-t border-border/50">
                      <div className="flex items-center justify-between text-xs text-muted-foreground font-mono">
                        <span>AI Agent: Claude · Status: Online</span>
                        <span>v1.0.0 · Base44 Design System {new Date().getFullYear()}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </main>
            </div>
          </div>
        </Providers>
      </body>
    </html>
  );
}