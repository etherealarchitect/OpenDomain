"use client";

import Link from "next/link";
import { useState } from "react";

export default function Home() {
  const [query, setQuery] = useState("");

  return (
    <div className="flex min-h-screen flex-col">
      <nav className="flex items-center justify-between px-6 py-4">
        <span className="font-mono text-sm tracking-tight text-ink-dim">
          opendomain
        </span>
        <div className="flex gap-6 text-sm text-ink-dim">
          <Link href="/dashboard" className="hover:text-ink transition-colors">
            Dashboard
          </Link>
          <Link href="/agent" className="hover:text-ink transition-colors">
            Agent
          </Link>
        </div>
      </nav>

      <main className="flex flex-1 flex-col items-center justify-center px-6 pb-24">
        <div className="w-full max-w-xl">
          <h1 className="mb-2 text-3xl font-semibold tracking-tight text-ink">
            Find your domain
          </h1>
          <p className="mb-8 text-ink-dim" style={{ maxWidth: "42ch" }}>
            Search, register, and manage domains from your own infrastructure.
            No vendor lock-in.
          </p>

          <div className="group relative">
            <div className="absolute -inset-px rounded-lg bg-edge opacity-0 transition-opacity group-focus-within:opacity-100" />
            <div className="relative flex items-center rounded-lg border border-edge bg-ground-raised">
              <span className="pl-4 font-mono text-sm text-ink-faint select-none">
                $
              </span>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="yourproject.dev"
                className="flex-1 bg-transparent px-3 py-4 font-mono text-sm text-ink placeholder:text-ink-faint focus:outline-none"
              />
              <button className="mr-2 rounded-md bg-focus px-4 py-2 text-sm font-medium text-ground hover:bg-focus/90 transition-colors">
                Search
              </button>
            </div>
          </div>

          <div className="mt-3 flex gap-3 font-mono text-xs text-ink-faint">
            <span>.com</span>
            <span>.dev</span>
            <span>.io</span>
            <span>.app</span>
            <span>.net</span>
            <span>.org</span>
            <span>.co</span>
          </div>
        </div>

        <div className="mt-20 grid w-full max-w-3xl grid-cols-1 gap-px overflow-hidden rounded-lg border border-edge bg-edge md:grid-cols-3">
          <Capability
            title="DNS management"
            detail="Full zone editor with templates for GitHub Pages, Vercel, Google Workspace, and more."
          />
          <Capability
            title="AI agent"
            detail="Describe what you need in plain language. The agent handles the API calls."
          />
          <Capability
            title="Terminal-first"
            detail="Complete CLI for every action. Pipe, script, automate."
          />
        </div>
      </main>

      <footer className="border-t border-edge px-6 py-4 text-center font-mono text-xs text-ink-faint">
        open source &middot; self-hosted &middot; yours
      </footer>
    </div>
  );
}

function Capability({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="bg-ground-raised p-5">
      <h3 className="text-sm font-medium text-ink">{title}</h3>
      <p className="mt-1 text-xs leading-relaxed text-ink-dim">{detail}</p>
    </div>
  );
}
