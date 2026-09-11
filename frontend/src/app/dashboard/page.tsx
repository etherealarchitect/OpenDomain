"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/shell";
import { api, type DomainResponse } from "@/lib/api";

export default function Dashboard() {
  const [domains, setDomains] = useState<DomainResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .listDomains()
      .then(setDomains)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const active = domains.filter((d) => d.status === "active");
  const expiring = domains.filter((d) => {
    const days =
      (new Date(d.expiry_date).getTime() - Date.now()) / (1000 * 60 * 60 * 24);
    return days < 30 && days > 0;
  });

  return (
    <Shell>
      <div className="mx-auto max-w-4xl px-6 py-10">
        <h1 className="text-2xl font-semibold tracking-tight text-ink">
          Dashboard
        </h1>

        <div className="mt-8 grid grid-cols-3 gap-px overflow-hidden rounded-lg border border-edge bg-edge">
          <Stat label="Domains" value={domains.length} />
          <Stat label="Active" value={active.length} />
          <Stat
            label="Expiring soon"
            value={expiring.length}
            alert={expiring.length > 0}
          />
        </div>

        <div className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <QuickAction href="/" label="Register domain" />
          <QuickAction href="/domains/transfer" label="Transfer in" />
          <QuickAction href="/domains" label="Manage DNS" />
          <QuickAction href="/agent" label="Ask Agent" />
        </div>

        <div className="mt-10">
          <div className="flex items-baseline justify-between">
            <h2 className="text-sm font-medium text-ink">Your domains</h2>
            <Link href="/" className="text-xs text-focus hover:underline">
              Register new
            </Link>
          </div>

          {loading ? (
            <p className="mt-6 text-sm text-ink-faint">Loading...</p>
          ) : domains.length === 0 ? (
            <div className="mt-6 rounded-lg border border-edge bg-ground-raised p-8 text-center">
              <p className="text-sm text-ink-dim">No domains yet.</p>
              <Link
                href="/"
                className="mt-2 inline-block text-sm text-focus hover:underline"
              >
                Search for one
              </Link>
            </div>
          ) : (
            <div className="mt-4 overflow-hidden rounded-lg border border-edge">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-edge bg-ground-raised text-xs text-ink-faint">
                    <th className="px-4 py-2 font-medium">Domain</th>
                    <th className="px-4 py-2 font-medium">Status</th>
                    <th className="px-4 py-2 font-medium">Expires</th>
                    <th className="px-4 py-2 font-medium text-right">Auto-renew</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-edge">
                  {domains.map((d) => (
                    <tr key={d.id} className="hover:bg-ground-raised/50">
                      <td className="px-4 py-3">
                        <Link
                          href={`/domains/${d.id}`}
                          className="font-mono text-sm text-ink hover:text-focus"
                        >
                          {d.name}
                        </Link>
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge status={d.status} />
                      </td>
                      <td className="px-4 py-3 font-mono text-xs text-ink-dim">
                        {new Date(d.expiry_date).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3 text-right text-xs text-ink-dim">
                        {d.auto_renew ? "on" : "off"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </Shell>
  );
}

function Stat({
  label,
  value,
  alert,
}: {
  label: string;
  value: number;
  alert?: boolean;
}) {
  return (
    <div className="bg-ground-raised px-5 py-4">
      <p
        className={`text-2xl font-semibold tabular-nums ${alert ? "text-caution" : "text-ink"}`}
      >
        {value}
      </p>
      <p className="mt-0.5 text-xs text-ink-dim">{label}</p>
    </div>
  );
}

function QuickAction({ href, label }: { href: string; label: string }) {
  return (
    <Link
      href={href}
      className="rounded-lg border border-edge bg-ground-raised px-4 py-3 text-center text-sm text-ink-dim transition-colors hover:text-ink hover:bg-ground-overlay"
    >
      {label}
    </Link>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    active: "text-live bg-live-dim",
    expired: "text-fault bg-fault/10",
    pendingTransfer: "text-caution bg-caution/10",
    pendingCreate: "text-focus bg-focus-dim",
  };
  return (
    <span
      className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${colors[status] || "text-ink-faint bg-ground-overlay"}`}
    >
      {status}
    </span>
  );
}
