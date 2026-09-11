"use client";

import { useState } from "react";
import { Search, User, HelpCircle, Bell, MessageSquare, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

export function TopBar() {
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <header className="z-10 flex h-14 items-center justify-between border-b border-border bg-background/80 backdrop-blur-sm px-6">
      {/* Left sidebar toggle would go here */}

      {/* Center: Search */}
      <div className="flex-1 max-w-md mx-auto">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <input
            type="search"
            placeholder="Search domains, DNS records, contacts..."
            className="w-full rounded-lg border border-border bg-sidebar-background/50 py-2 pl-9 pr-4 text-sm placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary/20"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-2">
        {/* Quick actions */}
        <button
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-border hover:bg-sidebar-background/50 transition-colors"
          aria-label="Quick actions"
        >
          <span>⌘</span>
          <span>K</span>
        </button>

        {/* Notifications */}
        <button
          className="relative flex h-8 w-8 items-center justify-center rounded-lg hover:bg-sidebar-background/50 transition-colors"
          aria-label="Notifications"
        >
          <Bell className="h-4 w-4 text-muted-foreground" />
          <span className="absolute -right-1 -top-1 inline-flex h-4 w-4 items-center justify-center rounded-full bg-accent text-[10px] font-medium text-white">
            3
          </span>
        </button>

        {/* User profile */}
        <button
          className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg hover:bg-sidebar-background/50 transition-colors"
          aria-label="User profile"
        >
          <div className="h-6 w-6 rounded-lg bg-gradient-to-br from-primary to-accent"></div>
          <span className="text-sm font-medium">Scott</span>
          <ChevronDown className="h-3 w-3 text-muted-foreground" />
        </button>
      </div>
    </header>
  );
}