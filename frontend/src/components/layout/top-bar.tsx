"use client";

import { useState } from "react";
import { Search, User, Bell, ChevronDown } from "lucide-react";
import { useAuth } from "@/lib/auth";
import { cn } from "@/lib/utils";

export function TopBar() {
  const [searchQuery, setSearchQuery] = useState("");
  const { user } = useAuth();

  return (
    <header className="z-10 flex h-14 items-center justify-between border-b border-[#e9e6f2]/30 bg-[#f8f7fe]/80 backdrop-blur-sm px-6">
      {/* Center: Search */}
      <div className="flex-1 max-w-md mx-auto">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[#1d1528]/60" />
          <input
            type="search"
            placeholder="Search domains, DNS records, contacts..."
            className="w-full bg-[#faf8ff]/50 rounded-lg px-3 py-2 border border-[#e9e6f2] flex-1 pl-9 text-sm placeholder:text-[#1d1528]/60 focus:outline-none focus:border-[#8a5bd1]/50"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-2">
        {/* Quick actions */}
        <button
          className="font-medium text-sm px-4 py-2 rounded-lg border border-[#e9e6f2] hover:border-[#e9e6f2]/60 bg-[#f8f7fe] hover:bg-[#faf8ff]/50 transition-all duration-200"
          aria-label="Quick actions"
        >
          <span className="font-mono">⌘K</span>
        </button>

        {/* Help */}
        <button
          className="h-7 w-7 flex items-center justify-center rounded-lg hover:bg-[#e9e6f2]/50 transition-colors border border-[#e9e6f2]"
          aria-label="Help"
        >
          <User className="h-3.5 w-3.5 text-[#1d1528]/60" />
        </button>

        {/* Notifications */}
        <div className="relative">
          <button
            className="h-7 w-7 flex items-center justify-center rounded-lg hover:bg-[#e9e6f2]/50 transition-colors border border-[#e9e6f2]"
            aria-label="Notifications"
          >
            <Bell className="h-3.5 w-3.5 text-[#1d1528]/60" />
          </button>
          <span className="absolute -right-1 -top-1 inline-flex h-4 w-4 items-center justify-center rounded-full bg-[#a855ef] text-[10px] font-medium text-white">
            3
          </span>
        </div>

        {/* User profile */}
        <button
          className="font-medium text-sm px-3 py-2 rounded-lg border border-[#e9e6f2] hover:border-[#e9e6f2]/60 bg-[#f8f7fe] hover:bg-[#faf8ff]/50 transition-all duration-200 flex items-center gap-2"
          aria-label="User profile"
        >
          <div className="h-5 w-5 rounded-lg bg-gradient-to-br from-[#8a5bd1] to-[#a855ef]"></div>
          {user && (
            <span className="text-sm font-medium text-[#1d1528]">
              {user.email?.split('@')[0] || "User"}
            </span>
          )}
          <ChevronDown className="h-3 w-3 text-[#1d1528]/60" />
        </button>
      </div>
    </header>
  );
}