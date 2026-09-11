"use client";

import Link from "next/link";
import { useParams, useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/shell";
import {
  api,
  type DomainResponse,
  type DnsZoneResponse,
  type DnsRecordCreate,
  type DnsTemplate,
} from "@/lib/api";
import { toast } from "@/components/ui/toast";

type Tab = "overview" | "dns" | "settings";

const TABS: { key: Tab; label: string }[] = [
  { key: "overview", label: "Overview" },
  { key: "dns", label: "DNS" },
  { key: "settings", label: "Settings" },
];

const RECORD_TYPES = ["A", "AAAA", "CNAME", "MX", "TXT", "NS", "SRV", "CAA"];

export default function DomainDetail() {
  const { id } = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const router = useRouter();
  const [domain, setDomain] = useState<DomainResponse | null>(null);
  const [zone, setZone] = useState<DnsZoneResponse | null>(null);
  const [templates, setTemplates] = useState<DnsTemplate[]>([]);
  const [loading, setLoading] = useState(true);

  const tab = (searchParams.get("tab") as Tab) || "overview";

  function setTab(t: Tab) {
    router.push(`/domains/${id}?tab=${t}`);
  }

  useEffect(() => {
    Promise.all([
      api.getDomain(id).catch(() => null),
      api.getDnsZone(id).catch(() => null),
      api.getDnsTemplates(id).catch(() => []),
    ]).then(([d, z, t]) => {
      setDomain(d);
      setZone(z);
      setTemplates(t);
      setLoading(false);
    });
  }, [id]);

  async function reloadZone() {
    const z = await api.getDnsZone(id).catch(() => null);
    setZone(z);
  }

  if (loading) {
    return (
      <Shell>
        <div className="flex min-h-[60vh] items-center justify-center">
          <p className="text-sm text-ink-faint">Loading...</p>
        </div>
      </Shell>
    );
  }

  if (!domain) {
    return (
      <Shell>
        <div className="flex min-h-[60vh] items-center justify-center">
          <p className="text-sm text-ink-faint">Domain not found.</p>
        </div>
      </Shell>
    );
  }

  return (
    <Shell>
      <div className="mx-auto max-w-4xl px-6 py-10">
        <div className="flex items-center gap-2">
          <Link href="/domains" className="text-xs text-ink-faint hover:text-ink transition-colors">
            Domains
          </Link>
          <span className="text-xs text-ink-faint">/</span>
        </div>

        <div className="mt-2 flex items-baseline gap-3">
          <h1 className="font-mono text-2xl font-semibold text-ink">{domain.name}</h1>
          <StatusBadge status={domain.status} />
        </div>

        <div className="mt-6 flex gap-1 border-b border-edge">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`border-b-2 px-4 py-2 text-sm transition-colors ${
                tab === t.key
                  ? "border-focus text-ink"
                  : "border-transparent text-ink-dim hover:text-ink"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        <div className="mt-6">
          {tab === "overview" && <OverviewTab domain={domain} />}
          {tab === "dns" && (
            <DnsTab
              domain={domain}
              zone={zone}
              templates={templates}
              onReload={reloadZone}
            />
          )}
          {tab === "settings" && (
            <SettingsTab domain={domain} onUpdate={setDomain} />
          )}
        </div>
      </div>
    </Shell>
  );
}

function OverviewTab({ domain }: { domain: DomainResponse }) {
  return (
    <div className="grid grid-cols-2 gap-6 md:grid-cols-4">
      <Field label="Registered" value={fmt(domain.registration_date)} />
      <Field label="Expires" value={fmt(domain.expiry_date)} />
      <Field label="Auto-renew" value={domain.auto_renew ? "on" : "off"} />
      <Field label="Privacy" value={domain.privacy_enabled ? "on" : "off"} />
      <Field label="Locked" value={domain.locked ? "yes" : "no"} />
      <Field label="Price" value={`$${(domain.price_cents / 100).toFixed(2)}`} />
      <Field label="Renewal" value={`$${(domain.renewal_price_cents / 100).toFixed(2)}/yr`} />
      <Field
        label="Nameservers"
        value={domain.nameservers?.replace(/,/g, "\n") || "default"}
        mono
      />
    </div>
  );
}

function DnsTab({
  domain,
  zone,
  templates,
  onReload,
}: {
  domain: DomainResponse;
  zone: DnsZoneResponse | null;
  templates: DnsTemplate[];
  onReload: () => Promise<void>;
}) {
  const [showForm, setShowForm] = useState(false);
  const [recordType, setRecordType] = useState("A");
  const [name, setName] = useState("");
  const [content, setContent] = useState("");
  const [ttl, setTtl] = useState("3600");
  const [priority, setPriority] = useState("10");
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState("");
  const [applyingTemplate, setApplyingTemplate] = useState(false);

  const needsPriority = recordType === "MX" || recordType === "SRV";

  async function addRecord(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const data: DnsRecordCreate = {
        record_type: recordType,
        name: name || "@",
        content,
        ttl: parseInt(ttl) || 3600,
      };
      if (needsPriority) data.priority = parseInt(priority) || 10;
      await api.createDnsRecord(domain.id, data);
      toast("Record added", "success");
      setShowForm(false);
      setName("");
      setContent("");
      await onReload();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to add record", "error");
    } finally {
      setSaving(false);
    }
  }

  async function deleteRecord(recordId: string) {
    setDeleting(recordId);
    try {
      await api.deleteDnsRecord(domain.id, recordId);
      toast("Record deleted", "success");
      await onReload();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to delete", "error");
    } finally {
      setDeleting(null);
    }
  }

  async function applyTemplate() {
    if (!selectedTemplate) return;
    setApplyingTemplate(true);
    try {
      await api.applyDnsTemplate(domain.id, selectedTemplate);
      toast(`Template "${selectedTemplate}" applied`, "success");
      setSelectedTemplate("");
      await onReload();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to apply template", "error");
    } finally {
      setApplyingTemplate(false);
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-medium text-ink">DNS Records</h2>
        <div className="flex gap-2">
          {templates.length > 0 && (
            <div className="flex gap-1">
              <select
                value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}
                className="rounded-md border border-edge bg-ground-raised px-2 py-1.5 text-xs text-ink focus:border-focus focus:outline-none"
              >
                <option value="">Apply template...</option>
                {templates.map((t) => (
                  <option key={t.name} value={t.name}>
                    {t.name} ({t.record_count} records)
                  </option>
                ))}
              </select>
              {selectedTemplate && (
                <button
                  onClick={applyTemplate}
                  disabled={applyingTemplate}
                  className="rounded-md bg-focus px-2 py-1.5 text-xs font-medium text-ground hover:bg-focus/90 disabled:opacity-50"
                >
                  {applyingTemplate ? "..." : "Apply"}
                </button>
              )}
            </div>
          )}
          <button
            onClick={() => setShowForm(!showForm)}
            className="rounded-md bg-focus px-3 py-1.5 text-xs font-medium text-ground hover:bg-focus/90 transition-colors"
          >
            {showForm ? "Cancel" : "Add record"}
          </button>
        </div>
      </div>

      {showForm && (
        <form onSubmit={addRecord} className="mt-4 rounded-lg border border-edge bg-ground-raised p-4">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <label className="flex flex-col gap-1">
              <span className="text-xs text-ink-dim">Type</span>
              <select
                value={recordType}
                onChange={(e) => setRecordType(e.target.value)}
                className="rounded-md border border-edge bg-ground px-2 py-1.5 text-sm text-ink focus:border-focus focus:outline-none"
              >
                {RECORD_TYPES.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-xs text-ink-dim">Name</span>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="@ or subdomain"
                className="rounded-md border border-edge bg-ground px-2 py-1.5 text-sm text-ink placeholder:text-ink-faint focus:border-focus focus:outline-none"
              />
            </label>
            <label className="flex flex-col gap-1 sm:col-span-2">
              <span className="text-xs text-ink-dim">Content</span>
              <input
                value={content}
                onChange={(e) => setContent(e.target.value)}
                required
                placeholder={recordType === "A" ? "192.168.1.1" : recordType === "CNAME" ? "example.com" : "value"}
                className="rounded-md border border-edge bg-ground px-2 py-1.5 text-sm text-ink placeholder:text-ink-faint focus:border-focus focus:outline-none"
              />
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-xs text-ink-dim">TTL</span>
              <input
                value={ttl}
                onChange={(e) => setTtl(e.target.value)}
                type="number"
                className="rounded-md border border-edge bg-ground px-2 py-1.5 text-sm text-ink focus:border-focus focus:outline-none"
              />
            </label>
            {needsPriority && (
              <label className="flex flex-col gap-1">
                <span className="text-xs text-ink-dim">Priority</span>
                <input
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                  type="number"
                  className="rounded-md border border-edge bg-ground px-2 py-1.5 text-sm text-ink focus:border-focus focus:outline-none"
                />
              </label>
            )}
          </div>
          <button
            type="submit"
            disabled={saving}
            className="mt-3 rounded-md bg-focus px-4 py-1.5 text-xs font-medium text-ground hover:bg-focus/90 disabled:opacity-50"
          >
            {saving ? "Adding..." : "Add record"}
          </button>
        </form>
      )}

      {zone && zone.records.length > 0 ? (
        <div className="mt-4 overflow-hidden rounded-lg border border-edge">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-edge bg-ground-raised text-xs text-ink-faint">
                <th className="px-4 py-2 font-medium">Type</th>
                <th className="px-4 py-2 font-medium">Name</th>
                <th className="px-4 py-2 font-medium">Content</th>
                <th className="px-4 py-2 font-medium text-right">TTL</th>
                <th className="px-4 py-2 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-edge font-mono text-xs">
              {zone.records.map((r) => (
                <tr key={r.id} className="hover:bg-ground-raised/50">
                  <td className="px-4 py-2 text-focus">{r.record_type}</td>
                  <td className="px-4 py-2 text-ink">{r.name}</td>
                  <td className="max-w-[200px] truncate px-4 py-2 text-ink-dim">{r.content}</td>
                  <td className="px-4 py-2 text-right text-ink-faint">{r.ttl}</td>
                  <td className="px-4 py-2 text-right">
                    <button
                      onClick={() => deleteRecord(r.id)}
                      disabled={deleting === r.id}
                      className="text-fault/60 hover:text-fault transition-colors disabled:opacity-50"
                    >
                      {deleting === r.id ? "..." : "delete"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="mt-4 text-sm text-ink-faint">
          No DNS records. Add one or apply a template above.
        </p>
      )}
    </div>
  );
}

function SettingsTab({
  domain,
  onUpdate,
}: {
  domain: DomainResponse;
  onUpdate: (d: DomainResponse) => void;
}) {
  const router = useRouter();
  const [renewing, setRenewing] = useState(false);
  const [authCode, setAuthCode] = useState<string | null>(null);
  const [loadingCode, setLoadingCode] = useState(false);

  async function toggle(field: "auto_renew" | "privacy_enabled" | "locked") {
    try {
      if (field === "locked") {
        const updated = domain.locked
          ? await api.unlockDomain(domain.id)
          : await api.lockDomain(domain.id);
        onUpdate(updated);
        toast(updated.locked ? "Domain locked" : "Domain unlocked", "success");
      } else {
        const updated = await api.updateDomain(domain.id, {
          [field]: !domain[field],
        });
        onUpdate(updated);
        toast("Setting updated", "success");
      }
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to update", "error");
    }
  }

  async function renewDomain() {
    setRenewing(true);
    try {
      const updated = await api.renewDomain(domain.id, 1);
      onUpdate(updated);
      toast("Domain renewed for 1 year", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to renew", "error");
    } finally {
      setRenewing(false);
    }
  }

  async function getAuthCode() {
    setLoadingCode(true);
    try {
      const { auth_code } = await api.getAuthCode(domain.id);
      setAuthCode(auth_code);
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to get auth code", "error");
    } finally {
      setLoadingCode(false);
    }
  }

  async function deleteDomain() {
    if (!confirm(`Delete ${domain.name}? This cannot be undone.`)) return;
    try {
      await api.deleteDomain(domain.id);
      toast(`${domain.name} deleted`, "success");
      router.push("/domains");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to delete", "error");
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-edge bg-ground-raised p-5">
        <h3 className="text-sm font-medium text-ink">Domain settings</h3>
        <div className="mt-4 space-y-4">
          <ToggleRow
            label="Auto-renew"
            description="Automatically renew before expiry"
            enabled={domain.auto_renew}
            onToggle={() => toggle("auto_renew")}
          />
          <ToggleRow
            label="WHOIS privacy"
            description="Hide personal information in WHOIS lookups"
            enabled={domain.privacy_enabled}
            onToggle={() => toggle("privacy_enabled")}
          />
          <ToggleRow
            label="Transfer lock"
            description="Prevent unauthorized transfers"
            enabled={domain.locked}
            onToggle={() => toggle("locked")}
          />
        </div>
      </div>

      <div className="rounded-lg border border-edge bg-ground-raised p-5">
        <h3 className="text-sm font-medium text-ink">Renew domain</h3>
        <p className="mt-1 text-xs text-ink-dim">
          Current expiry: {fmt(domain.expiry_date)} &middot; Renewal: ${(domain.renewal_price_cents / 100).toFixed(2)}/yr
        </p>
        <button
          onClick={renewDomain}
          disabled={renewing}
          className="mt-3 rounded-md bg-focus px-4 py-2 text-sm font-medium text-ground hover:bg-focus/90 disabled:opacity-50"
        >
          {renewing ? "Renewing..." : "Renew for 1 year"}
        </button>
      </div>

      <div className="rounded-lg border border-edge bg-ground-raised p-5">
        <h3 className="text-sm font-medium text-ink">Auth code</h3>
        <p className="mt-1 text-xs text-ink-dim">
          Required for transferring this domain to another registrar.
        </p>
        {authCode ? (
          <p className="mt-3 rounded-md border border-edge bg-ground px-3 py-2 font-mono text-sm text-ink">
            {authCode}
          </p>
        ) : (
          <button
            onClick={getAuthCode}
            disabled={loadingCode}
            className="mt-3 rounded-md border border-edge px-4 py-2 text-sm text-ink-dim hover:text-ink hover:bg-ground-overlay transition-colors disabled:opacity-50"
          >
            {loadingCode ? "Loading..." : "Reveal auth code"}
          </button>
        )}
      </div>

      <div className="rounded-lg border border-fault/20 bg-fault/5 p-5">
        <h3 className="text-sm font-medium text-fault">Danger zone</h3>
        <p className="mt-1 text-xs text-ink-dim">
          Permanently delete this domain. This action cannot be undone.
        </p>
        <button
          onClick={deleteDomain}
          className="mt-3 rounded-md border border-fault/30 px-4 py-2 text-sm text-fault hover:bg-fault/10 transition-colors"
        >
          Delete domain
        </button>
      </div>
    </div>
  );
}

function ToggleRow({
  label,
  description,
  enabled,
  onToggle,
}: {
  label: string;
  description: string;
  enabled: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-ink">{label}</p>
        <p className="text-xs text-ink-faint">{description}</p>
      </div>
      <button
        onClick={onToggle}
        className={`relative h-5 w-9 rounded-full transition-colors ${enabled ? "bg-live" : "bg-edge"}`}
      >
        <span
          className={`absolute top-0.5 left-0.5 h-4 w-4 rounded-full bg-white transition-transform ${
            enabled ? "translate-x-4" : "translate-x-0"
          }`}
        />
      </button>
    </div>
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

function Field({
  label,
  value,
  mono,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div>
      <p className="text-xs text-ink-faint">{label}</p>
      <p className={`mt-1 text-sm text-ink whitespace-pre-line ${mono ? "font-mono" : ""}`}>
        {value}
      </p>
    </div>
  );
}

function fmt(iso: string) {
  return new Date(iso).toLocaleDateString("en-AU", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}
