"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { Sidebar } from "./sidebar";
import { TopBar } from "./top-bar";

export function Shell({ children }: { children: React.ReactNode }) {
  const { user, loading, init, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    init();
  }, [init]);

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [loading, user, router]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#f8f7fe]">
        <div className="flex flex-col items-center">
          <div className="relative">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-[#8a5bd1] to-[#a855ef]"></div>
            <div className="absolute -inset-2 bg-gradient-to-r from-[#8a5bd1]/20 to-[#a855ef]/20 blur-xl opacity-40 animate-pulse"></div>
          </div>
          <p className="mt-4 text-sm text-[#1d1528]/70 font-body">Loading OpenDomain...</p>
        </div>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="flex min-h-screen bg-[#f8f7fe]">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <TopBar />
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}