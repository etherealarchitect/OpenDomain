"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth";

const NAV = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/domains", label: "Domains" },
  { href: "/contacts", label: "Contacts" },
  { href: "/agent", label: "Agent" },
  { href: "/account", label: "Account" },
];

export function Shell({ children }: { children: React.ReactNode }) {
  const { user, loading, init, logout } = useAuth();
  const pathname = usePathname();
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
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-ink-faint">Loading...</p>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="flex min-h-screen">
      <aside className="fixed left-0 top-0 flex h-full w-52 flex-col border-r border-edge bg-ground px-3 py-4">
        <Link
          href="/dashboard"
          className="mb-8 px-2 font-mono text-sm tracking-tight text-ink-dim"
        >
          opendomain
        </Link>

        <nav className="flex flex-col gap-0.5">
          {NAV.map((item) => {
            const active = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded-md px-2 py-1.5 text-sm transition-colors ${
                  active
                    ? "bg-ground-raised text-ink"
                    : "text-ink-dim hover:text-ink hover:bg-ground-raised/50"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto border-t border-edge pt-3">
          <p className="truncate px-2 text-xs text-ink-dim">{user.email}</p>
          <button
            onClick={() => {
              logout();
              router.push("/login");
            }}
            className="mt-1 w-full rounded-md px-2 py-1.5 text-left text-xs text-ink-faint hover:text-ink hover:bg-ground-raised/50 transition-colors"
          >
            Sign out
          </button>
        </div>
      </aside>

      <main className="ml-52 flex-1">{children}</main>
    </div>
  );
}
