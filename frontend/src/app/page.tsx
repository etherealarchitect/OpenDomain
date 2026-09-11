import { Lato, Open_Sans, JetBrains_Mono } from "next/font/google";

const lato = Lato({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-lato",
  weight: ["300", "400", "700", "900"],
});

const openSans = Open_Sans({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-open-sans",
  weight: ["300", "400", "500", "600", "700", "800"],
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-jetbrains-mono",
});

export default function Home() {
  return (
    <div className={`${lato.variable} ${openSans.variable} ${jetbrainsMono.variable}`}>
      <header className="absolute top-0 left-0 right-0 border-b border-border/30 bg-background/80 backdrop-blur-sm">
        <nav className="max-w-7xl mx-auto p-6 sm:p-8 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="relative">
              <div className="absolute -inset-2 bg-gradient-to-r from-primary/20 to-accent/20 blur-xl opacity-40"></div>
              <svg
                viewBox="0 0 32 32"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="relative h-8 w-8 text-primary"
              >
                <circle cx="16" cy="16" r="12" fill="currentColor" opacity="0.2" />
                <path
                  d="M16 6L22 12L16 18L10 12L16 6Z"
                  fill="currentColor"
                />
                <circle cx="16" cy="16" r="2" fill="white" />
              </svg>
            </div>
            <div>
              <div className="text-base font-heading font-bold tracking-tight text-foreground">
                OpenDomain
              </div>
              <div className="text-xs font-mono text-muted-foreground tracking-tight mt-0.5">
                AI-Powered Domain Management
              </div>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button className="font-medium text-sm px-4 py-2 rounded-lg border border-border hover:border-border/60 bg-background hover:bg-sidebar-background/50 transition-all duration-200">
              Sign In
            </button>
            <button className="font-medium text-sm px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-all duration-200 shadow-sm hover:shadow-md">
              Get Started
            </button>
          </div>
        </nav>
      </header>

      <main className="min-h-screen flex flex-col items-center justify-center px-6 py-12 sm:py-16 md:py-24">
        <div className="max-w-7xl mx-auto w-full">
          <div className="relative">
            <div className="absolute -inset-12 bg-gradient-radial from-primary/10 via-transparent to-transparent opacity-40"></div>
            <div className="absolute -inset-12 bg-gradient-to-br from-accent/5 via-transparent to-primary/5 blur-3xl opacity-50"></div>

            <div className="relative z-10 text-center">
              <div className="mb-8 inline-flex items-center gap-2 font-mono text-xs text-muted-foreground px-3 py-1.5 rounded-full border border-border bg-background/50 backdrop-blur-sm">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent/70"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
                </span>
                <span>Active AI Agent Session</span>
              </div>

              <h1 className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl 2xl:text-7xl font-heading font-black tracking-tighter text-foreground mb-6">
                Manage Your
                <span className="block bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
                  Domain Fleet
                </span>
              </h1>

              <p className="text-base sm:text-lg lg:text-xl text-muted-foreground mb-10 max-w-xl mx-auto leading-relaxed">
                Search, register, configure DNS, monitor uptime, and trade domains—all from a single
                AI-powered terminal interface.
              </p>

              <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-8 mb-10 shadow-xl">
                <div className="absolute top-0 left-6 -translate-y-1/2 bg-background px-4 py-1.5 rounded-full border border-border">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs">AI Terminal</span>
                    <div className="flex gap-1">
                      <span className="w-3 h-3 rounded-full bg-destructive"></span>
                      <span className="w-3 h-3 rounded-full bg-yellow-500"></span>
                      <span className="w-3 h-3 rounded-full bg-green-500"></span>
                    </div>
                  </div>
                </div>

                <div className="bg-[hsl(262_25%_5%)] border border-border rounded-lg font-mono text-sm">
                  <div className="flex items-center px-4 py-3 border-b border-border bg-[hsl(262_25%_8%)]">
                    <span className="text-muted-foreground">$</span>
                    <div className="flex-1 ml-2">
                      <div className="flex items-center gap-2">
                        <span className="text-primary">opendomain</span>
                        <span className="text-muted-foreground">agent</span>
                      </div>
                    </div>
                    <div className="flex gap-1">
                      <span className="w-3 h-3 rounded-full bg-destructive"></span>
                      <span className="w-3 h-3 rounded-full bg-yellow-500"></span>
                      <span className="w-3 h-3 rounded-full bg-green-500"></span>
                    </div>
                  </div>

                  <div className="p-4 overflow-auto">
                    <div className="space-y-3">
                      <div className="flex gap-2 items-center">
                        <span className="text-accent-foreground">&gt;</span>
                        <div className="bg-sidebar-background/50 rounded-lg px-3 py-2 border border-border flex-1">
                          <input
                            type="text"
                            placeholder="Find domains for my new AI startup"
                            className="w-full bg-transparent text-foreground placeholder:text-muted-foreground focus:outline-none"
                            autoComplete="off"
                            autoFocus
                          />
                        </div>
                      </div>

                      <div className="flex gap-2 items-center">
                        <span className="text-accent-foreground">✓</span>
                        <div className="bg-sidebar-background/50 rounded-lg px-3 py-2 border border-border flex-1">
                          <div className="flex items-center gap-2 text-muted-foreground">
                            <span>Searching available domains...</span>
                            <div className="flex items-center gap-1">
                              <span className="w-2 h-2 rounded-full bg-accent animate-pulse"></span>
                              <span className="w-2 h-2 rounded-full bg-accent animate-pulse delay-150"></span>
                              <span className="w-2 h-2 rounded-full bg-accent animate-pulse delay-300"></span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="text-xs text-muted-foreground flex items-center gap-2 p-4 border-t border-border">
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-sidebar-background rounded-lg border border-border">
                      <span>⌘</span>
                      <span>Enter</span>
                      <span className="text-accent">to execute</span>
                    </span>
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-sidebar-background rounded-lg border border-border">
                      <span>↑</span>
                      <span>↓</span>
                      <span className="text-accent">to navigate</span>
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap gap-3 justify-center">
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-sidebar-background/50 border border-border">
                  <span className="text-xs text-accent">✓</span>
                  <span className="text-sm">Real-time Domain Search</span>
                </div>
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-sidebar-background/50 border border-border">
                  <span className="text-xs text-accent">✓</span>
                  <span className="text-sm">AI-Powered DNS Config</span>
                </div>
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-sidebar-background/50 border border-border">
                  <span className="text-xs text-accent">✓</span>
                  <span className="text-sm">Terminal-First Interface</span>
                </div>
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-sidebar-background/50 border border-border">
                  <span className="text-xs text-accent">✓</span>
                  <span className="text-sm">Open Source & Self-Hosted</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-16 text-center">
          <div className="text-xs font-mono text-muted-foreground mb-2">
            Built with Claude AI • FastAPI • Next.js • PostgreSQL
          </div>
          <div className="text-2xs font-mono text-muted-foreground/60">
            Version 1.0.0 • Platform Status: Operational
          </div>
        </div>
      </main>

      <footer className="absolute bottom-0 left-0 right-0 p-6 sm:p-8 border-t border-border/30">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4 text-xs text-muted-foreground font-medium">
            <span>Documentation</span>
            <span>API</span>
            <span>CLI</span>
            <span>Status</span>
            <span>GitHub</span>
            <span>Twitter</span>
          </div>
          <div className="text-2xs font-mono text-muted-foreground/60">
            © 2024 OpenDomain • AGPL-3.0 License • opendomain.etherealcode.org
          </div>
        </div>
      </footer>
    </div>
  );
}