"use client";

import { useState } from "react";
import { Shell } from "@/components/layout/shell";
import { api, type WhoisResult } from "@/lib/api";
import { toast } from "@/components/ui/toast";

export default function WhoisPage() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<WhoisResult | null>(null);
  const [loading, setLoading] = useState(false);

  async function lookup(e: React.FormEvent) {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;
    setLoading(true);
    setResult(null);
    try {
      const data = await api.whoisLookup(q);
      setResult(data);
    } catch (err) {
      toast(err instanceof Error ? err.message : "Lookup failed", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Shell>
      <div className="mx-auto max-w-3xl px-6 py-8">
        <h1 className="text-xl font-semibold text-ink">WHOIS Lookup</h1>
        <p className="mt-1 text-sm text-ink-dim">
          Look up registration details for any domain.
        </p>

        <form onSubmit={lookup} className="mt-6">
          <div className="flex items-center gap-2 rounded-lg border border-edge bg-ground-raised">
            <span className="pl-4 font-mono text-sm text-ink-faint select-none">whois</span>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="example.com"
              className="flex-1 bg-transparent px-3 py-3 font-mono text-sm text-ink placeholder:text-ink-faint focus:outline-none"
            />
            <button
              type="submit"
              disabled={loading}
              className="mr-2 rounded-md bg-focus px-4 py-2 text-sm font-medium text-ground transition-colors hover:bg-focus/90 disabled:opacity-50"
            >
              {loading ? "Looking up..." : "Lookup"}
            </button>
          </div>
        </form>

        {result && (
          <div className="mt-6 rounded-lg border border-edge bg-ground-raised p-5">
            <div className="flex items-center justify-between gap-3">
              <h2 className="font-mono text-sm font-medium text-ink">{result.domain_name}</h2>
              <span className={`rounded-full px-2 py-0.5 font-mono text-xs ${result.lookup_status === "registered" ? "bg-emerald-500/15 text-emerald-400" : result.lookup_status === "not_found" ? "bg-ground-overlay text-ink-faint" : result.lookup_status === "available" ? "bg-amber-500/15 text-amber-300" : "bg-ground-overlay text-ink-faint"}`}>
                {result.lookup_status}
              </span>
            </div>
            <p className="mt-2 text-xs text-ink-faint">Source: {result.source.toUpperCase()}</p>
            {(result.lookup_status === "unknown" || result.lookup_status === "not_found") && (
              <p className="mt-3 rounded-md border border-amber-500/20 bg-amber-500/5 px-3 py-2 text-xs text-amber-200">
                {result.lookup_status === "not_found"
                  ? "No registration was found. Registrability is not established; check with the intended registry."
                  : "Registration status could not be confirmed. This does not indicate that the domain is available."}
              </p>
            )}
            <dl className="mt-4 space-y-3 text-sm">
              <Row label="Registrar" value={result.registrar || "Unknown"} />
              <Row label="DNSSEC" value={result.dnssec === null ? "Unknown" : result.dnssec ? "Signed" : "Not signed"} />
              <Row label="Created" value={result.creation_date ? new Date(result.creation_date).toLocaleDateString("en-AU", { year: "numeric", month: "short", day: "numeric" }) : "Unknown"} />
              <Row label="Expires" value={result.expiration_date ? new Date(result.expiration_date).toLocaleDateString("en-AU", { year: "numeric", month: "short", day: "numeric" }) : "Unknown"} />
              {result.nameservers && result.nameservers.length > 0 && (
                <div className="flex justify-between">
                  <dt className="text-ink-dim">Nameservers</dt>
                  <dd className="text-right font-mono text-ink">
                    {result.nameservers.map((ns, i) => (
                      <span key={i} className="block">{ns}</span>
                    ))}
                  </dd>
                </div>
              )}
              {result.status && result.status.length > 0 && (
                <div>
                  <dt className="text-xs text-ink-dim mb-1">Status</dt>
                  <dd className="flex flex-wrap gap-1">
                    {result.status.map((s, i) => (
                      <span key={i} className="rounded-full bg-ground-overlay px-2 py-0.5 font-mono text-xs text-ink-faint">{s}</span>
                    ))}
                  </dd>
                </div>
              )}
            </dl>
            {result.warnings.length > 0 && (
              <div className="mt-4 rounded-md border border-amber-500/20 bg-amber-500/5 px-3 py-2 text-xs text-amber-200">
                {result.warnings.map((warning) => <p key={warning}>{warning}</p>)}
              </div>
            )}
          </div>
        )}
      </div>
    </Shell>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <dt className="text-ink-dim">{label}</dt>
      <dd className="text-ink">{value}</dd>
    </div>
  );
}
