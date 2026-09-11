import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";
import { Sidebar } from "@/components/layout/sidebar";
import { TopBar } from "@/components/layout/top-bar";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-jetbrains-mono",
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
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`} suppressHydrationWarning>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
        <meta name="theme-color" content="#111113" />
      </head>
      <body className="min-h-screen bg-background font-sans text-sm text-text-primary antialiased overflow-hidden">
        <Providers>
          <div className="flex h-screen overflow-hidden">
            <Sidebar />
            <div className="flex-1 flex flex-col overflow-hidden">
              <TopBar />
              <main className="flex-1 overflow-auto p-6 lg:p-8">{children}</main>
            </div>
          </div>
        </Providers>
      </body>
    </html>
  );
}