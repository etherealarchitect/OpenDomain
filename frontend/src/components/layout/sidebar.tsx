"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";
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
  LogOut,
  Cloud,
  Database,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: Home },
  { href: "/domains", label: "Domains", icon: Globe },
  { href: "/contacts", label: "Contacts", icon: Users },
  { href: "/agent", label: "AI Agent", icon: Bot },
  { href: "/whois", label: "WHOIS", icon: Search },
  { href: "/monitoring", label: "Monitoring", icon: Eye },
  { href: "/marketplace", label: "Marketplace", icon: Store },
  { href: "/dns", label: "DNS", icon: Server },
  { href: "/security", label: "Security", icon: Shield },
  { href: "/billing", label: "Billing", icon: Wallet },
];

const BOTTOM_NAV_ITEMS = [
  { href: "/settings", label: "Settings", icon: Settings },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/api", label: "API", icon: Cpu },
  { href: "/cli", label: "CLI", icon: Terminal },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <aside
      className={cn(
        "flex flex-col border-r border-[#e9e6f2] bg-[#faf8ff] transition-all duration-300 backdrop-blur-sm",
        isCollapsed ? "w-16" : "w-64"
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-[#e9e6f2]">
        <div className="flex items-center justify-between">
          {!isCollapsed && (
            <Link href="/dashboard" className="flex items-center gap-3 group">
              <div className="relative">
                <div className="absolute -inset-2 bg-gradient-to-r from-[#8a5bd1]/20 to-[#a855ef]/20 blur-xl opacity-40 group-hover:opacity-60 transition-opacity"></div>
                <div className="relative h-8 w-8 rounded-lg bg-gradient-to-br from-[#8a5bd1] to-[#a855ef] flex items-center justify-center">
                  <Globe className="h-4 w-4 text-white" />
                </div>
              </div>
              <div>
                <div className="font-heading font-bold text-[#1d1528] text-sm">OpenDomain</div>
                <div className="font-mono text-[10px] text-[#1d1528]/70 tracking-tight">AI Terminal</div>
              </div>
            </Link>
          )}
          {isCollapsed && (
            <Link href="/dashboard" className="mx-auto">
              <div className="relative h-8 w-8 rounded-lg bg-gradient-to-br from-[#8a5bd1] to-[#a855ef] flex items-center justify-center">
                <Globe className="h-4 w-4 text-white" />
              </div>
            </Link>
          )}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="h-7 w-7 flex items-center justify-center rounded-lg hover:bg-[#e9e6f2]/50 transition-colors border border-[#e9e6f2]"
            aria-label={isCollapsed ? "Expand" : "Collapse"}
          >
            {isCollapsed ? (
              <ChevronRight className="h-3 w-3 text-[#1d1528]/70" />
            ) : (
              <ChevronLeft className="h-3 w-3 text-[#1d1528]/70" />
            )}
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-3">
        <div className="space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/");

            return (
              <Link
                key={item.label}
                href={item.href}
                className={cn(
                  "group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-all duration-200",
                  isActive
                    ? "bg-gradient-to-r from-[#8a5bd1]/10 to-[#a855ef]/5 border border-[#8a5bd1]/20 text-[#8a5bd1] shadow-sm"
                    : "text-[#1d1528]/70 hover:text-[#1d1528] hover:bg-[#e9e6f2]/20 border border-transparent hover:border-[#e9e6f2]"
                )}
              >
                <div className="relative">
                  <Icon className={cn(
                    "h-4 w-4",
                    isActive ? "text-[#8a5bd1]" : "text-[#1d1528]/70 group-hover:text-[#1d1528]"
                  )} />
                </div>
                {!isCollapsed && (
                  <span className="font-medium">{item.label}</span>
                )}
                {isCollapsed && isActive && (
                  <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 bg-gradient-to-r from-[#8a5bd1]/10 to-[#a855ef]/5 border border-[#8a5bd1]/20 px-2 py-1 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                    <span className="text-xs font-medium text-[#8a5bd1] whitespace-nowrap">{item.label}</span>
                  </div>
                )}
              </Link>
            );
          })}
        </div>

        <div className="mt-4 pt-4 border-t border-[#e9e6f2]">
          <div className="space-y-1">
            {BOTTOM_NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;

              return (
                <Link
                  key={item.label}
                  href={item.href}
                  className={cn(
                    "group flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
                    isActive
                      ? "text-[#8a5bd1] bg-[#8a5bd1]/5"
                      : "text-[#1d1528]/60 hover:text-[#1d1528] hover:bg-[#e9e6f2]/20"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {!isCollapsed && (
                    <span className="font-medium">{item.label}</span>
                  )}
                </Link>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Status */}
      <div className="p-3 border-t border-[#e9e6f2]">
        {!isCollapsed ? (
          <div className="px-3 py-2 rounded-lg border border-[#e9e6f2] bg-[#f8f7fe]">
            <div className="flex items-center justify-between">
              <div className="text-xs font-medium text-[#1d1528]">Status</div>
              <div className="flex items-center gap-1.5">
                <div className="h-1.5 w-1.5 rounded-full bg-[#10b981]"></div>
                <span className="text-[10px] font-medium text-[#1d1528]/60">Online</span>
              </div>
            </div>
            <div className="mt-1 text-[10px] font-mono text-[#1d1528]/60 truncate">
              API v1.0.0
            </div>
          </div>
        ) : (
          <div className="flex justify-center">
            <div className="h-2 w-2 rounded-full bg-[#10b981]"></div>
          </div>
        )}
      </div>
    </aside>
  );
}