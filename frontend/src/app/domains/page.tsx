"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { Shell } from "@/components/layout/shell";
import { api, type DomainResponse } from "@/lib/api";
import { toast } from "@/components/ui/toast";

type StatusFilter = "all" | "active" | "expired" | "pendingCreate" | "pendingTransfer";

const FILTERS: { key: StatusFilter; label: string }[] = [
  { key: "all", label: "All" },
  { key: "active", label: "Active" },
  { key: "expired", label: "Expired" },
  { key: "pendingCreate", label: "Pending" },
];

export default function DomainsPage() {
  const [domains, setDomains] = useState<DomainResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<StatusFilter>("all");
  const [search, setSearch] = useState("");

  useEffect(() => {
    api
      .listDomains()
      .then(setDomains)
      .catch((e) => toast(e.message, "error"))
      .finally(() => setLoading(false));
  }, []);

  const filtered = domains.filter((d) => {
    if (filter !== "all" && d.status !== filter) return false;
    if (search && !d.name.includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <Shell>
      <div className="mx-auto max-w-5xl px-6 py-8">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-ink">Domains</h1>
          <div className="flex gap-2">
            <Link
              href="/domains/transfer"
              className="rounded-md border border-edge px-3 py-1.5 text-sm text-ink-dim hover:text-ink hover:bg-ground-raised transition-colors"
            >
              Transfer in
            </Link>
            <Link
              href="/"
              className="rounded-md bg-focus px-3 py-1.5 text-sm font-medium text-ground hover:bg-focus/90 transition-colors"
            >
              Register new
            </Link>
          </div>
        </div>

        <div className="mt-6 flex items-center gap-4">
          <div className="flex gap-1 rounded-md border border-edge bg-ground-raised p-0.5">
            {FILTERS.map((f) => (
              <button
                key={f.key}
                onClick={() => setFilter(f.key)}
                className={`rounded px-2.5 py-1 text-xs transition-colors ${
                  filter === f.key
                    ? "bg-ground-overlay text-ink"
                    : "text-ink-faint hover:text-ink-dim"
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter domains..."
            className="rounded-md border border-edge bg-ground-raised px-3 py-1.5 text-sm text-ink placeholder:text-ink-faint focus:border-focus focus:outline-none focus:ring-1 focus:ring-focus"
          />
        </div>

        {loading ? (
          <p className="mt-10 text-sm text-ink-faint">Loading domains...</p>
        ) : filtered.length === 0 ? (
          <div className="mt-10 rounded-lg border border-edge bg-ground-raised p-10 text-center">
            {domains.length === 0 ? (
              <>
                <p className="text-sm text-ink-dim">No domains registered yet.</p>
                <Link
                  href="/"
                  className="mt-2 inline-block text-sm text-focus hover:underline"
                >
                  Search for a domain
                </Link>
              </>
            ) : (
              <p className="text-sm text-ink-dim">
                No domains match your filters.
              </p>
            )}
          </div>
        ) : (
          <div className="mt-4 overflow-hidden rounded-lg border border-edge">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-edge bg-ground-raised text-xs text-ink-faint">
                  <th className="px-4 py-2.5 font-medium">Domain</th>
                  <th className="px-4 py-2.5 font-medium">Status</th>
                  <th className="px-4 py-2.5 font-medium">Expires</th>
                  <th className="px-4 py-2.5 font-medium">Auto-renew</th>
                  <th className="px-4 py-2.5 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-edge">
                {filtered.map((d) => (
                  <DomainRow key={d.id} domain={d} onUpdate={setDomains} allDomains={domains} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Shell>
  );
}

function DomainRow({
  domain: d,
  onUpdate,
  allDomains,
}: {
  domain: DomainResponse;
  onUpdate: (d: DomainResponse[]) => void;
  allDomains: DomainResponse[];
}) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [toggling, setToggling] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function close(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setMenuOpen(false);
    }
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);

  async function toggleAutoRenew() {
    setToggling(true);
    try {
      const updated = await api.updateDomain(d.id, { auto_renew: !d.auto_renew });
      onUpdate(allDomains.map((x) => (x.id === d.id ? updated : x)));
      toast(`Auto-renew ${updated.auto_renew ? "enabled" : "disabled"}`, "success");
    } catch (e) {
      toast(e instanceof Error ? e.message : "Failed to update", "error");
    } finally {
      setToggling(false);
    }
  }

  async function handleDelete() {
    if (!confirm(`Delete ${d.name}? This action cannot be undone.`)) return;
    try {
      await api.deleteDomain(d.id);
      onUpdate(allDomains.filter((x) => x.id !== d.id));
      toast(`${d.name} deleted`, "success");
    } catch (e) {
      toast(e instanceof Error ? e.message : "Failed to delete", "error");
    }
  }

  const daysLeft = Math.ceil(
    (new Date(d.expiry_date).getTime() - Date.now()) / (1000 * 60 * 60 * 24),
  );

  return (
    <tr className="hover:bg-ground-raised/50">
      <td className="px-4 py-3">
        <Link
          href={`/domains/${d.id}`}
          className="font-mono text-sm text-ink hover:text-focus transition-colors"
        >
          {d.name}
        </Link>
      </td>
      <td className="px-4 py-3">
        <StatusBadge status={d.status} />
      </td>
      <td className="px-4 py-3">
        <span className="font-mono text-xs text-ink-dim">
          {new Date(d.expiry_date).toLocaleDateString("en-AU", {
            year: "numeric",
            month: "short",
            day: "numeric",
          })}
        </span>
        {daysLeft > 0 && daysLeft < 30 && (
          <span className="ml-2 text-xs text-caution">{daysLeft}d left</span>
        )}
      </td>
      <td className="px-4 py-3">
        <button
          onClick={toggleAutoRenew}
          disabled={toggling}
          className={`relative h-5 w-9 rounded-full transition-colors ${
            d.auto_renew ? "bg-live" : "bg-edge"
          } ${toggling ? "opacity-50" : ""}`}
        >
          <span
            className={`absolute top-0.5 left-0.5 h-4 w-4 rounded-full bg-white transition-transform ${
              d.auto_renew ? "translate-x-4" : "translate-x-0"
            }`}
          />
        </button>
      </td>
      <td className="px-4 py-3 text-right">
        <div className="relative inline-block" ref={ref}>
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="rounded-md px-2 py-1 text-xs text-ink-faint hover:text-ink hover:bg-ground-overlay transition-colors"
          >
            &middot;&middot;&middot;
          </button>
          {menuOpen && (
            <div className="absolute right-0 top-full z-10 mt-1 w-36 rounded-md border border-edge bg-ground-raised py-1 shadow-lg">
              <Link
                href={`/domains/${d.id}?tab=dns`}
                className="block px-3 py-1.5 text-xs text-ink-dim hover:text-ink hover:bg-ground-overlay transition-colors"
              >
                DNS records
              </Link>
              <Link
                href={`/domains/${d.id}?tab=settings`}
                className="block px-3 py-1.5 text-xs text-ink-dim hover:text-ink hover:bg-ground-overlay transition-colors"
              >
                Settings
              </Link>
              <Link
                href={`/domains/${d.id}?tab=settings&action=renew`}
                className="block px-3 py-1.5 text-xs text-ink-dim hover:text-ink hover:bg-ground-overlay transition-colors"
              >
                Renew
              </Link>
              <button
                onClick={handleDelete}
                className="w-full px-3 py-1.5 text-left text-xs text-fault hover:bg-ground-overlay transition-colors"
              >
                Delete
              </button>
            </div>
          )}
        </div>
      </td>
    </tr>
  );
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    active: "text-live bg-live-dim",
    expired: "text-fault bg-fault/10",
    pendingTransfer: "text-caution bg-caution/10",
    pendingCreate: "text-focus bg-focus-dim",
    pendingDelete: "text-fault bg-fault/10",
    suspended: "text-ink-faint bg-ground-overlay",
  };
  return (
    <span
      className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${map[status] || "text-ink-faint bg-ground-overlay"}`}
    >
      {status}
    </span>
  );
}
