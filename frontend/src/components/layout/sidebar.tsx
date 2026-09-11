"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Bot,
  Globe,
  Server,
  Search,
  Eye,
  BarChart3,
  Settings,
  Users,
  Wallet,
  Home,
  Store,
  Lock,
  Terminal,
  Cpu,
  Shield,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { title: "Dashboard", href: "/dashboard", icon: Home },
  {
    title: "AI Agent",
    href: "/agent",
    icon: Bot,
    badge: "21",
    active: true,
  },
  { title: "Domains", href: "/domains", icon: Globe },
  { title: "DNS", href: "/dns", icon: Server },
  { title: "WHOIS", href: "/whois", icon: Search },
  { title: "Monitoring", href: "/monitoring", icon: Eye },
  { title: "Marketplace", href: "/marketplace", icon: Store },
  { title: "Security", href: "/security", icon: Shield },
  { title: "CLI", href: "/cli", icon: Terminal },
];

const bottomNavItems = [
  { title: "Settings", href: "/settings", icon: Settings },
  { title: "Analytics", href: "/analytics", icon: BarChart3 },
  { title: "API", href: "/api", icon: Cpu },
];

export function Sidebar() {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <aside
      className={cn(
        "flex flex-col border-r border-border bg-sidebar-background transition-all duration-300 backdrop-blur-sm",
        isCollapsed ? "w-16" : "w-64"
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-border/30">
        <div className="flex items-center justify-between">
          {!isCollapsed && (
            <Link href="/" className="flex items-center gap-3 group">
              <div className="relative">
                <div className="absolute -inset-2 bg-gradient-to-r from-primary/20 to-accent/20 blur-xl opacity-40 group-hover:opacity-60 transition-opacity"></div>
                <div className="relative h-8 w-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
                  <Globe className="h-4 w-4 text-white" />
                </div>
              </div>
              <div>
                <div className="font-heading font-bold text-foreground text-sm">OpenDomain</div>
                <div className="font-mono text-[10px] text-muted-foreground tracking-tight">AI Terminal</div>
              </div>
            </Link>
          )}
          {isCollapsed && (
            <Link href="/" className="mx-auto">
              <div className="relative h-8 w-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
                <Globe className="h-4 w-4 text-white" />
              </div>
            </Link>
          )}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="h-7 w-7 flex items-center justify-center rounded-lg hover:bg-border/50 transition-colors border border-border"
            aria-label={isCollapsed ? "Expand" : "Collapse"}
          >
            {isCollapsed ? (
              <ChevronRight className="h-3 w-3 text-muted-foreground" />
            ) : (
              <ChevronLeft className="h-3 w-3 text-muted-foreground" />
            )}
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-3">
        <div className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/");

            return (
              <Link
                key={item.title}
                href={item.href}
                className={cn(
                  "group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-all duration-200",
                  isActive || item.active
                    ? "bg-gradient-to-r from-primary/10 to-accent/5 border border-primary/20 text-primary shadow-sm"
                    : "text-muted-foreground hover:text-foreground hover:bg-border/20 border border-transparent hover:border-border"
                )}
              >
                <div className="relative">
                  <Icon className={cn(
                    "h-4 w-4",
                    (isActive || item.active) ? "text-primary" : "text-muted-foreground group-hover:text-foreground"
                  )} />
                  {item.badge && (
                    <span className="absolute -top-1.5 -right-1.5 h-4 w-4 flex items-center justify-center rounded-full bg-accent text-[10px] font-medium text-white">
                      {item.badge}
                    </span>
                  )}
                </div>
                {!isCollapsed && (
                  <span className="font-medium">{item.title}</span>
                )}
                {isCollapsed && item.active && (
                  <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 bg-gradient-to-r from-primary/10 to-accent/5 border border-primary/20 px-2 py-1 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                    <span className="text-xs font-medium text-primary whitespace-nowrap">{item.title}</span>
                  </div>
                )}
              </Link>
            );
          })}
        </div>

        <div className="mt-4 pt-4 border-t border-border/30">
          <div className="space-y-1">
            {bottomNavItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;

              return (
                <Link
                  key={item.title}
                  href={item.href}
                  className={cn(
                    "group flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
                    isActive
                      ? "text-primary bg-primary/5"
                      : "text-muted-foreground hover:text-foreground hover:bg-border/20"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {!isCollapsed && <span>{item.title}</span>}
                </Link>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Status */}
      <div className="p-3 border-t border-border/30">
        {!isCollapsed ? (
          <div className="px-3 py-2 rounded-lg border border-border bg-background/80">
            <div className="flex items-center justify-between">
              <div className="text-xs font-medium text-foreground">Status</div>
              <div className="flex items-center gap-1.5">
                <div className="h-1.5 w-1.5 rounded-full bg-green-500"></div>
                <span className="text-[10px] font-medium text-muted-foreground">Online</span>
              </div>
            </div>
            <div className="mt-1 text-[10px] font-mono text-muted-foreground truncate">
              API v1.0.0
            </div>
          </div>
        ) : (
          <div className="flex justify-center">
            <div className="h-2 w-2 rounded-full bg-green-500"></div>
          </div>
        )}
      </div>
    </aside>
  );
}