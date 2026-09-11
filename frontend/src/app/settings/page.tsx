"use client";

import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/shell";
import {
  api,
  type WebhookResponse,
  type ApiKeyResponse,
  type ApiKeyCreatedResponse,
} from "@/lib/api";
import { toast } from "@/components/ui/toast";

type Tab = "webhooks" | "apikeys";

const WEBHOOK_EVENTS = [
  "DOMAIN_REGISTERED", "DOMAIN_RENEWED", "DOMAIN_EXPIRED", "DOMAIN_TRANSFERRED",
  "DOMAIN_DELETED", "DNS_CHANGED", "SSL_EXPIRING", "UPTIME_DOWN", "UPTIME_UP",
];

export default function SettingsPage() {
  const [tab, setTab] = useState<Tab>("webhooks");
  const [webhooks, setWebhooks] = useState<WebhookResponse[]>([]);
  const [apiKeys, setApiKeys] = useState<ApiKeyResponse[]>([]);
  const [loading, setLoading] = useState(true);

  const [showWebhookForm, setShowWebhookForm] = useState(false);
  const [webhookUrl, setWebhookUrl] = useState("");
  const [webhookEvents, setWebhookEvents] = useState<string[]>([]);

  const [showKeyForm, setShowKeyForm] = useState(false);
  const [keyName, setKeyName] = useState("");
  const [newKey, setNewKey] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api.listWebhooks().catch(() => []),
      api.listApiKeys().catch(() => []),
    ]).then(([w, k]) => {
      setWebhooks(w);
      setApiKeys(k);
      setLoading(false);
    });
  }, []);

  async function createWebhook(e: React.FormEvent) {
    e.preventDefault();
    if (!webhookUrl.trim() || webhookEvents.length === 0) return;
    try {
      const wh = await api.createWebhook(webhookUrl.trim(), webhookEvents);
      setWebhooks((prev) => [wh, ...prev]);
      setShowWebhookForm(false);
      setWebhookUrl("");
      setWebhookEvents([]);
      toast("Webhook created", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed", "error");
    }
  }

  async function deleteWebhook(id: string) {
    try {
      await api.deleteWebhook(id);
      setWebhooks((prev) => prev.filter((w) => w.id !== id));
      toast("Webhook deleted", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed", "error");
    }
  }

  async function createApiKey(e: React.FormEvent) {
    e.preventDefault();
    if (!keyName.trim()) return;
    try {
      const result = await api.createApiKey(keyName.trim());
      setNewKey(result.key);
      setApiKeys((prev) => [result, ...prev]);
      setKeyName("");
      toast("API key created — copy it now, it won't be shown again", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed", "error");
    }
  }

  async function revokeApiKey(id: string) {
    try {
      await api.revokeApiKey(id);
      setApiKeys((prev) => prev.filter((k) => k.id !== id));
      toast("API key revoked", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed", "error");
    }
  }

  function toggleEvent(event: string) {
    setWebhookEvents((prev) =>
      prev.includes(event) ? prev.filter((e) => e !== event) : [...prev, event],
    );
  }

  return (
    <Shell>
      <div className="mx-auto max-w-4xl px-6 py-8">
        <h1 className="text-xl font-semibold text-ink">Settings</h1>

        <div className="mt-6 flex gap-1 rounded-md border border-edge bg-ground-raised p-0.5">
          {(["webhooks", "apikeys"] as Tab[]).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`rounded px-3 py-1.5 text-xs transition-colors ${
                tab === t ? "bg-ground-overlay text-ink" : "text-ink-faint hover:text-ink-dim"
              }`}
            >
              {t === "webhooks" ? "Webhooks" : "API Keys"}
            </button>
          ))}
        </div>

        {loading ? (
          <p className="mt-8 text-sm text-ink-faint">Loading...</p>
        ) : (
          <div className="mt-6">
            {tab === "webhooks" && (
              <>
                <div className="flex items-center justify-between">
                  <p className="text-sm text-ink-dim">
                    Receive HTTP callbacks when events occur.
                  </p>
                  <button onClick={() => setShowWebhookForm(true)} className="rounded-md bg-focus px-3 py-1.5 text-xs font-medium text-ground transition-colors hover:bg-focus/90">
                    Add webhook
                  </button>
                </div>

                {showWebhookForm && (
                  <form onSubmit={createWebhook} className="mt-4 rounded-lg border border-edge bg-ground-raised p-5">
                    <label className="flex flex-col gap-1">
                      <span className="text-xs text-ink-dim">Endpoint URL</span>
                      <input type="url" required value={webhookUrl} onChange={(e) => setWebhookUrl(e.target.value)} placeholder="https://example.com/webhook" className="rounded-md border border-edge bg-ground px-3 py-1.5 font-mono text-sm text-ink placeholder:text-ink-faint focus:border-focus focus:outline-none focus:ring-1 focus:ring-focus" />
                    </label>
                    <div className="mt-3">
                      <span className="text-xs text-ink-dim">Events</span>
                      <div className="mt-1 flex flex-wrap gap-1.5">
                        {WEBHOOK_EVENTS.map((ev) => (
                          <button key={ev} type="button" onClick={() => toggleEvent(ev)} className={`rounded-full px-2 py-0.5 text-xs transition-colors ${webhookEvents.includes(ev) ? "bg-focus text-ground" : "bg-ground-overlay text-ink-faint hover:text-ink-dim"}`}>
                            {ev.replace(/_/g, " ").toLowerCase()}
                          </button>
                        ))}
                      </div>
                    </div>
                    <div className="mt-4 flex gap-2">
                      <button type="submit" className="rounded-md bg-focus px-4 py-2 text-sm font-medium text-ground transition-colors hover:bg-focus/90">Create</button>
                      <button type="button" onClick={() => setShowWebhookForm(false)} className="rounded-md border border-edge px-4 py-2 text-sm text-ink-dim transition-colors hover:bg-ground-overlay">Cancel</button>
                    </div>
                  </form>
                )}

                <div className="mt-4 space-y-2">
                  {webhooks.length === 0 ? (
                    <div className="rounded-lg border border-edge bg-ground-raised p-8 text-center">
                      <p className="text-sm text-ink-dim">No webhooks configured.</p>
                    </div>
                  ) : (
                    webhooks.map((wh) => (
                      <div key={wh.id} className="flex items-start justify-between rounded-lg border border-edge bg-ground-raised p-4">
                        <div>
                          <p className="font-mono text-sm text-ink">{wh.url}</p>
                          <p className="mt-1 text-xs text-ink-faint">
                            Events: {wh.events.split(",").map((e) => e.trim().replace(/_/g, " ").toLowerCase()).join(", ")}
                          </p>
                          {wh.failure_count > 0 && (
                            <p className="mt-0.5 text-xs text-caution">{wh.failure_count} failed deliveries</p>
                          )}
                        </div>
                        <button onClick={() => deleteWebhook(wh.id)} className="text-xs text-ink-faint hover:text-fault transition-colors">Delete</button>
                      </div>
                    ))
                  )}
                </div>
              </>
            )}

            {tab === "apikeys" && (
              <>
                <div className="flex items-center justify-between">
                  <p className="text-sm text-ink-dim">
                    Programmatic access to the OpenDomain API.
                  </p>
                  <button onClick={() => setShowKeyForm(true)} className="rounded-md bg-focus px-3 py-1.5 text-xs font-medium text-ground transition-colors hover:bg-focus/90">
                    Create key
                  </button>
                </div>

                {showKeyForm && (
                  <form onSubmit={createApiKey} className="mt-4 rounded-lg border border-edge bg-ground-raised p-5">
                    <label className="flex flex-col gap-1">
                      <span className="text-xs text-ink-dim">Key name</span>
                      <input type="text" required value={keyName} onChange={(e) => setKeyName(e.target.value)} placeholder="My CI/CD key" className="rounded-md border border-edge bg-ground px-3 py-1.5 text-sm text-ink placeholder:text-ink-faint focus:border-focus focus:outline-none focus:ring-1 focus:ring-focus" />
                    </label>
                    <div className="mt-4 flex gap-2">
                      <button type="submit" className="rounded-md bg-focus px-4 py-2 text-sm font-medium text-ground transition-colors hover:bg-focus/90">Create</button>
                      <button type="button" onClick={() => { setShowKeyForm(false); setNewKey(null); }} className="rounded-md border border-edge px-4 py-2 text-sm text-ink-dim transition-colors hover:bg-ground-overlay">Cancel</button>
                    </div>
                  </form>
                )}

                {newKey && (
                  <div className="mt-4 rounded-lg border border-caution/30 bg-caution/5 p-4">
                    <p className="text-xs font-medium text-caution">Copy your API key now — it won&apos;t be shown again.</p>
                    <div className="mt-2 flex items-center gap-2 rounded-md bg-ground p-2">
                      <code className="flex-1 break-all font-mono text-xs text-ink">{newKey}</code>
                      <button
                        onClick={() => { navigator.clipboard.writeText(newKey); toast("Copied", "success"); }}
                        className="shrink-0 rounded border border-edge px-2 py-1 text-xs text-ink-dim hover:text-ink transition-colors"
                      >
                        Copy
                      </button>
                    </div>
                  </div>
                )}

                <div className="mt-4 space-y-2">
                  {apiKeys.length === 0 ? (
                    <div className="rounded-lg border border-edge bg-ground-raised p-8 text-center">
                      <p className="text-sm text-ink-dim">No API keys.</p>
                    </div>
                  ) : (
                    apiKeys.map((k) => (
                      <div key={k.id} className="flex items-center justify-between rounded-lg border border-edge bg-ground-raised p-4">
                        <div>
                          <p className="text-sm font-medium text-ink">{k.name}</p>
                          <p className="mt-0.5 text-xs text-ink-faint">
                            <span className="font-mono">{k.prefix}...</span>
                            {k.last_used ? ` · Last used: ${new Date(k.last_used).toLocaleDateString("en-AU")}` : " · Never used"}
                            {k.expires_at && ` · Expires: ${new Date(k.expires_at).toLocaleDateString("en-AU")}`}
                          </p>
                        </div>
                        <button onClick={() => revokeApiKey(k.id)} className="text-xs text-ink-faint hover:text-fault transition-colors">Revoke</button>
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
