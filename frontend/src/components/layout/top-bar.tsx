"use client";

import { useState } from "react";
import { Search, User, HelpCircle, Bell, MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils";

export function TopBar() {
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <header className="z-10 flex h-14 items-center justify-between border-b border-surface-border bg-surface px-6">
      {/* Left: Search */}
      <div className="flex flex-1 items-center gap-4">
        <div className="relative max-w-md flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-tertiary" />
          <input
            type="search"
            placeholder="Search domains, DNS records, contacts..."
            className="w-full rounded-md border border-surface-border bg-surface-raised py-2 pl-9 pr-4 text-sm placeholder:text-text-tertiary focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-3">
        {/* Help */}
        <button
          className="relative flex h-8 w-8 items-center justify-center rounded-md hover:bg-surface-raised transition-colors"
          aria-label="Help"
        >
          <HelpCircle className="h-4 w-4 text-text-secondary" />
        </button>

        {/* Chat */}
        <button
          className="relative flex h-8 w-8 items-center justify-center rounded-md hover:bg-surface-raised transition-colors"
          aria-label="Chat"
        >
          <MessageSquare className="h-4 w-4 text-text-secondary" />
        </button>

        {/* Notifications */}
        <button
          className="relative flex h-8 w-8 items-center justify-center rounded-md hover:bg-surface-raised transition-colors"
          aria-label="Notifications"
        >
          <Bell className="h-4 w-4 text-text-secondary" />
          <span className="absolute -right-1 -top-1 inline-flex h-4 w-4 items-center justify-center rounded-full bg-primary-500 text-[10px] font-medium text-white">
            3
          </span>
        </button>

        {/* User profile */}
        <button
          className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-primary-600 to-primary-800"
          aria-label="User profile"
        >
          <User className="h-4 w-4 text-white" />
        </button>
      </div>
    </header>
  );
}