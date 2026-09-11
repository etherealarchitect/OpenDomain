"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { Shell } from "@/components/layout/shell";
import { api, type DomainSearchResult } from "@/lib/api";
import { toast } from "@/components/ui/toast";

function SearchContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const initialQuery = searchParams.get("q") || "";

  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState<DomainSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  async function doSearch(q: string) {
    const trimmed = q.trim();
    if (!trimmed) return;
    setLoading(true);
    setSearched(true);
    try {
      const data = await api.searchDomains(trimmed);
      setResults(data);
    } catch (e) {
      toast(e instanceof Error ? e.message : "Search failed", "error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (initialQuery) doSearch(initialQuery);
  }, [initialQuery]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) return;
    router.replace(`/domains/search?q=${encodeURIComponent(trimmed)}`);
    doSearch(trimmed);
  }

  return (
    <Shell>
      <div className="mx-auto max-w-3xl px-6 py-8">
        <h1 className="text-xl font-semibold text-ink">Domain Search</h1>

        <form onSubmit={handleSubmit} className="mt-6">
          <div className="flex items-center gap-2 rounded-lg border border-edge bg-ground-raised">
            <span className="pl-4 font-mono text-sm text-ink-faint select-none">
              $
            </span>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="yourproject.dev"
              className="flex-1 bg-transparent px-3 py-3 font-mono text-sm text-ink placeholder:text-ink-faint focus:outline-none"
            />
            <button
              type="submit"
              disabled={loading}
              className="mr-2 rounded-md bg-focus px-4 py-2 text-sm font-medium text-ground transition-colors hover:bg-focus/90 disabled:opacity-50"
            >
              {loading ? "Searching..." : "Search"}
            </button>
          </div>
        </form>

        {loading && (
          <p className="mt-10 text-center text-sm text-ink-faint">
            Checking availability...
          </p>
        )}

        {!loading && searched && results.length === 0 && (
          <div className="mt-10 rounded-lg border border-edge bg-ground-raised p-10 text-center">
            <p className="text-sm text-ink-dim">No results found.</p>
            <p className="mt-1 text-xs text-ink-faint">
              Try a different domain name or check your spelling.
            </p>
          </div>
        )}

        {!loading && results.length > 0 && (
          <div className="mt-6 overflow-hidden rounded-lg border border-edge">
            {results.map((r) => (
              <div
                key={r.domain}
                className="flex items-center justify-between border-b border-edge px-4 py-3.5 last:border-b-0 hover:bg-ground-raised/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm text-ink">{r.domain}</span>
                  {r.premium && (
                    <span className="rounded-full bg-caution/10 px-2 py-0.5 text-xs font-medium text-caution">
                      Premium
                    </span>
                  )}
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                      r.available
                        ? "bg-live-dim text-live"
                        : "bg-fault/10 text-fault"
                    }`}
                  >
                    {r.available ? "Available" : "Taken"}
                  </span>
                </div>

                <div className="flex items-center gap-4">
                  {r.price_cents != null && (
                    <span className="font-mono text-sm text-ink-dim">
                      ${(r.price_cents / 100).toFixed(2)}
                    </span>
                  )}
                  {r.available ? (
                    <Link
                      href={`/domains/register?domain=${encodeURIComponent(r.domain)}`}
                      className="rounded-md bg-focus px-3 py-1.5 text-xs font-medium text-ground transition-colors hover:bg-focus/90"
                    >
                      Register
                    </Link>
                  ) : (
                    <span className="rounded-md border border-edge px-3 py-1.5 text-xs text-ink-faint">
                      Unavailable
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Shell>
  );
}

export default function SearchPage() {
  return (
    <Suspense>
      <SearchContent />
    </Suspense>
  );
}
