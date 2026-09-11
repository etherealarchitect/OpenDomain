"use client";

import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/shell";
import {
  api,
  type AlertResponse,
  type UptimeCheckResponse,
  type DomainWatchResponse,
} from "@/lib/api";
import { toast } from "@/components/ui/toast";

type Tab = "alerts" | "uptime" | "watches";

export default function MonitoringPage() {
  const [tab, setTab] = useState<Tab>("alerts");
  const [alerts, setAlerts] = useState<AlertResponse[]>([]);
  const [uptimeChecks, setUptimeChecks] = useState<UptimeCheckResponse[]>([]);
  const [watches, setWatches] = useState<DomainWatchResponse[]>([]);
  const [loading, setLoading] = useState(true);

  const [watchDomain, setWatchDomain] = useState("");
  const [uptimeUrl, setUptimeUrl] = useState("");

  useEffect(() => {
    Promise.all([
      api.listAlerts().catch(() => []),
      api.listUptimeChecks().catch(() => []),
      api.listDomainWatches().catch(() => []),
    ]).then(([a, u, w]) => {
      setAlerts(a);
      setUptimeChecks(u);
      setWatches(w);
      setLoading(false);
    });
  }, []);

  async function addWatch(e: React.FormEvent) {
    e.preventDefault();
    if (!watchDomain.trim()) return;
    try {
      const w = await api.createDomainWatch(watchDomain.trim());
      setWatches((prev) => [w, ...prev]);
      setWatchDomain("");
      toast("Watch created", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed", "error");
    }
  }

  async function acknowledgeAlert(id: string) {
    try {
      await api.acknowledgeAlert(id);
      setAlerts((prev) => prev.map((a) => a.id === id ? { ...a, status: "acknowledged" } : a));
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed", "error");
    }
  }

  const TABS: { key: Tab; label: string }[] = [
    { key: "alerts", label: `Alerts (${alerts.length})` },
    { key: "uptime", label: `Uptime (${uptimeChecks.length})` },
    { key: "watches", label: `Watches (${watches.length})` },
  ];

  return (
    <Shell>
      <div className="mx-auto max-w-4xl px-6 py-8">
        <h1 className="text-xl font-semibold text-ink">Monitoring</h1>

        <div className="mt-6 flex gap-1 rounded-md border border-edge bg-ground-raised p-0.5">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`rounded px-3 py-1.5 text-xs transition-colors ${
                tab === t.key ? "bg-ground-overlay text-ink" : "text-ink-faint hover:text-ink-dim"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {loading ? (
          <p className="mt-8 text-sm text-ink-faint">Loading...</p>
        ) : (
          <div className="mt-6">
            {tab === "alerts" && (
              <div className="space-y-2">
                {alerts.length === 0 ? (
                  <Empty text="No alerts. All clear." />
                ) : (
                  alerts.map((a) => (
                    <div key={a.id} className="flex items-start justify-between rounded-lg border border-edge bg-ground-raised p-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <TypeBadge type={a.alert_type} />
                          <StatusBadge status={a.status} />
                        </div>
                        <p className="mt-1 text-sm text-ink">{a.title}</p>
                        <p className="mt-0.5 text-xs text-ink-faint">{a.message}</p>
                        <p className="mt-1 text-xs text-ink-faint">
                          {new Date(a.created_at).toLocaleString("en-AU")}
                        </p>
                      </div>
                      {a.status === "pending" && (
                        <button
                          onClick={() => acknowledgeAlert(a.id)}
                          className="shrink-0 rounded-md border border-edge px-2 py-1 text-xs text-ink-dim hover:text-ink hover:bg-ground-overlay transition-colors"
                        >
                          Acknowledge
                        </button>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}

            {tab === "uptime" && (
              <div className="space-y-2">
                {uptimeChecks.length === 0 ? (
                  <Empty text="No uptime checks configured." />
                ) : (
                  uptimeChecks.map((c) => (
                    <div key={c.id} className="flex items-center justify-between rounded-lg border border-edge bg-ground-raised p-4">
                      <div>
                        <p className="font-mono text-sm text-ink">{c.url}</p>
                        <p className="mt-0.5 text-xs text-ink-faint">
                          {c.last_checked ? `Last checked: ${new Date(c.last_checked).toLocaleString("en-AU")}` : "Never checked"}
                          {c.response_time_ms != null && ` · ${c.response_time_ms}ms`}
                        </p>
                      </div>
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                        c.status === "UP" ? "bg-live-dim text-live" :
                        c.status === "DOWN" ? "bg-fault/10 text-fault" :
                        "bg-ground-overlay text-ink-faint"
                      }`}>
                        {c.status}
                      </span>
                    </div>
                  ))
                )}
              </div>
            )}

            {tab === "watches" && (
              <>
                <form onSubmit={addWatch} className="flex gap-2">
                  <input
                    type="text"
                    value={watchDomain}
                    onChange={(e) => setWatchDomain(e.target.value)}
                    placeholder="domain-to-watch.com"
                    className="flex-1 rounded-md border border-edge bg-ground-raised px-3 py-2 font-mono text-sm text-ink placeholder:text-ink-faint focus:border-focus focus:outline-none focus:ring-1 focus:ring-focus"
                  />
                  <button
                    type="submit"
                    className="rounded-md bg-focus px-4 py-2 text-sm font-medium text-ground transition-colors hover:bg-focus/90"
                  >
                    Watch
                  </button>
                </form>
                <div className="mt-4 space-y-2">
                  {watches.length === 0 ? (
                    <Empty text="No domain watches. Add one above." />
                  ) : (
                    watches.map((w) => (
                      <div key={w.id} className="flex items-center justify-between rounded-lg border border-edge bg-ground-raised p-4">
                        <div>
                          <p className="font-mono text-sm text-ink">{w.domain_name}</p>
                          <p className="mt-0.5 text-xs text-ink-faint">
                            {w.last_checked ? `Checked: ${new Date(w.last_checked).toLocaleString("en-AU")}` : "Not yet checked"}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                            w.is_available ? "bg-live-dim text-live" : "bg-fault/10 text-fault"
                          }`}>
                            {w.is_available ? "Available" : "Taken"}
                          </span>
                          <button
                            onClick={async () => {
                              await api.deleteDomainWatch(w.id);
                              setWatches((prev) => prev.filter((x) => x.id !== w.id));
                            }}
                            className="text-xs text-ink-faint hover:text-fault transition-colors"
                          >
                            Remove
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </Shell>
  );
}

function Empty({ text }: { text: string }) {
  return (
    <div className="rounded-lg border border-edge bg-ground-raised p-8 text-center">
      <p className="text-sm text-ink-dim">{text}</p>
    </div>
  );
}

function TypeBadge({ type }: { type: string }) {
  const colors: Record<string, string> = {
    EXPIRY_WARNING: "bg-caution/10 text-caution",
    DNS_CHANGE: "bg-focus-dim text-focus",
    UPTIME_DOWN: "bg-fault/10 text-fault",
    SSL_EXPIRY: "bg-caution/10 text-caution",
    DOMAIN_AVAILABLE: "bg-live-dim text-live",
  };
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${colors[type] || "bg-ground-overlay text-ink-faint"}`}>
      {type.replace(/_/g, " ").toLowerCase()}
    </span>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    pending: "bg-caution/10 text-caution",
    sent: "bg-focus-dim text-focus",
    acknowledged: "bg-ground-overlay text-ink-faint",
  };
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${colors[status] || "bg-ground-overlay text-ink-faint"}`}>
      {status}
    </span>
  );
}
