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
  Bell,
  BarChart3,
  Settings,
  Users,
  Wallet,
  Home,
  Store,
  Mail,
  Lock,
  MessageSquare,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  {
    title: "Dashboard",
    href: "/",
    icon: Home,
    badge: null,
  },
  {
    title: "AI Agent",
    href: "/agent",
    icon: Bot,
    badge: "21",
    description: "Natural language control",
  },
  {
    title: "Domains",
    href: "/domains",
    icon: Globe,
    subItems: [
      { title: "My Domains", href: "/domains" },
      { title: "Search & Register", href: "/domains/search" },
      { title: "Transfers", href: "/domains/transfers" },
      { title: "Renewals", href: "/domains/renewals" },
    ],
  },
  {
    title: "DNS",
    href: "/dns",
    icon: Server,
    subItems: [
      { title: "Zones", href: "/dns" },
      { title: "Templates", href: "/dns/templates" },
      { title: "Import/Export", href: "/dns/import" },
    ],
  },
  {
    title: "WHOIS Lookup",
    href: "/whois",
    icon: Search,
  },
  {
    title: "Monitoring",
    href: "/monitoring",
    icon: Eye,
    subItems: [
      { title: "Domain Watches", href: "/monitoring/watches" },
      { title: "Uptime Checks", href: "/monitoring/uptime" },
      { title: "SSL Certificates", href: "/monitoring/ssl" },
      { title: "Alerts", href: "/monitoring/alerts" },
    ],
  },
  {
    title: "Marketplace",
    href: "/marketplace",
    icon: Store,
  },
  {
    title: "Contacts",
    href: "/contacts",
    icon: Users,
  },
  {
    title: "Billing",
    href: "/billing",
    icon: Wallet,
    subItems: [
      { title: "Invoices", href: "/billing/invoices" },
      { title: "Payment Methods", href: "/billing/payment-methods" },
      { title: "API Keys", href: "/billing/api-keys" },
    ],
  },
  {
    title: "Email Forwarding",
    href: "/email",
    icon: Mail,
  },
  {
    title: "SSL Certificates",
    href: "/ssl",
    icon: Lock,
  },
];

const bottomNavItems = [
  {
    title: "Settings",
    href: "/settings",
    icon: Settings,
  },
  {
    title: "Analytics",
    href: "/analytics",
    icon: BarChart3,
  },
  {
    title: "Notifications",
    href: "/notifications",
    icon: Bell,
    badge: "3",
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [expandedItems, setExpandedItems] = useState<string[]>([]);

  const toggleExpand = (title: string) => {
    setExpandedItems((prev) =>
      prev.includes(title) ? prev.filter((item) => item !== title) : [...prev, title]
    );
  };

  return (
    <aside
      className={cn(
        "flex flex-col border-r border-surface-border bg-surface transition-all duration-300",
        isCollapsed ? "w-16" : "w-64"
      )}
    >
      {/* Header */}
      <div className="border-b border-surface-border p-4">
        <div className="flex items-center justify-between">
          {!isCollapsed && (
            <Link href="/" className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary-600 to-primary-800">
                <Globe className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="font-bold text-base tracking-tight">OpenDomain</h1>
                <p className="text-[10px] text-text-tertiary">AI-Powered Domain Management</p>
              </div>
            </Link>
          )}
          {isCollapsed && (
            <Link href="/" className="mx-auto flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary-600 to-primary-800">
              <Globe className="h-5 w-5 text-white" />
            </Link>
          )}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="hidden lg:flex h-8 w-8 items-center justify-center rounded-md hover:bg-surface-raised transition-colors"
            aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        <div className="space-y-1 px-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
            const isExpanded = expandedItems.includes(item.title);
            const hasSubItems = item.subItems;

            return (
              <div key={item.title} className="relative">
                <button
                  onClick={() => {
                    if (hasSubItems) {
                      toggleExpand(item.title);
                    }
                  }}
                  className={cn(
                    "flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-sm transition-colors hover:bg-surface-raised",
                    isActive && !hasSubItems && "bg-surface-raised text-primary-400",
                    !isActive && !hasSubItems && "text-text-secondary hover:text-text-primary",
                    hasSubItems && "text-text-secondary hover:text-text-primary"
                  )}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={cn("h-4 w-4 shrink-0", isActive && !hasSubItems && "text-primary-400")} />
                    {!isCollapsed && (
                      <span className="font-medium">{item.title}</span>
                    )}
                  </div>
                  {!isCollapsed && (
                    <div className="flex items-center gap-2">
                      {item.badge && (
                        <span className="inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-primary-500/10 px-1.5 text-xs font-medium text-primary-400">
                          {item.badge}
                        </span>
                      )}
                      {item.description && !hasSubItems && (
                        <span className="hidden text-xs text-text-tertiary lg:inline">
                          {item.description}
                        </span>
                      )}
                      {hasSubItems && (
                        <ChevronRight
                          className={cn(
                            "h-4 w-4 transition-transform",
                            isExpanded && "rotate-90"
                          )}
                        />
                      )}
                    </div>
                  )}
                </button>
                {hasSubItems && !isCollapsed && (
                  <div
                    className={cn(
                      "overflow-hidden transition-all duration-200",
                      isExpanded ? "max-h-96" : "max-h-0"
                    )}
                  >
                    <div className="mt-1 pl-11 space-y-1">
                      {item.subItems.map((subItem) => (
                        <Link
                          key={subItem.title}
                          href={subItem.href}
                          className={cn(
                            "block rounded-md px-3 py-2 text-sm transition-colors hover:bg-surface-overlay hover:text-text-primary",
                            pathname === subItem.href
                              ? "text-primary-400"
                              : "text-text-tertiary"
                          )}
                        >
                          {subItem.title}
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
                {isCollapsed && (
                  <div className="absolute -right-2 top-1/2 z-10 hidden -translate-y-1/2 rounded-md border border-surface-border bg-surface px-3 py-2 text-sm shadow-lg group-hover:block">
                    <div className="font-medium text-text-primary">{item.title}</div>
                    {item.description && (
                      <div className="mt-1 max-w-xs text-xs text-text-tertiary">
                        {item.description}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Divider */}
        <div className="my-4 px-3">
          <div className="h-px bg-surface-border" />
        </div>

        {/* Bottom Navigation */}
        <div className="space-y-1 px-2">
          {bottomNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;

            return (
              <Link
                key={item.title}
                href={item.href}
                className={cn(
                  "group relative flex items-center justify-between rounded-lg px-3 py-2.5 text-sm transition-colors",
                  isActive
                    ? "bg-surface-raised text-primary-400"
                    : "text-text-secondary hover:bg-surface-raised hover:text-text-primary"
                )}
              >
                <div className="flex items-center gap-3">
                  <Icon className="h-4 w-4 shrink-0" />
                  {!isCollapsed && <span>{item.title}</span>}
                </div>
                {!isCollapsed && item.badge && (
                  <span className="inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-primary-500/10 px-1.5 text-xs font-medium text-primary-400">
                    {item.badge}
                  </span>
                )}
                {isCollapsed && item.badge && (
                  <span className="absolute -right-1 -top-1 inline-flex h-4 w-4 items-center justify-center rounded-full bg-primary-500 text-[10px] font-medium text-white">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </div>
      </nav>

      {/* User Profile */}
      <div className="border-t border-surface-border p-4">
        {!isCollapsed ? (
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-primary-600 to-primary-800" />
            <div className="flex-1 overflow-hidden">
              <p className="font-medium text-sm truncate">Scott K Brown</p>
              <p className="text-xs text-text-tertiary truncate">scott@example.com</p>
            </div>
          </div>
        ) : (
          <div className="flex justify-center">
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-primary-600 to-primary-800" />
          </div>
        )}
      </div>
    </aside>
  );
}