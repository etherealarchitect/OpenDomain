"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import {
  api,
  type DomainResponse,
  type DnsZoneResponse,
  type DnsRecordCreate,
} from "@/lib/api";

export default function DomainDetail() {
  const { id } = useParams<{ id: string }>();
  const [domain, setDomain] = useState<DomainResponse | null>(null);
  const [zone, setZone] = useState<DnsZoneResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getDomain(id).catch(() => null),
      api.getDnsZone(id).catch(() => null),
    ]).then(([d, z]) => {
      setDomain(d);
      setZone(z);
      setLoading(false);
    });
  }, [id]);

  if (loading) return <Loading />;
  if (!domain) return <NotFound />;

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <div className="flex items-baseline gap-3">
        <h1 className="font-mono text-2xl font-semibold text-ink">
          {domain.name}
        </h1>
        <span
          className={`rounded-full px-2 py-0.5 text-xs font-medium ${
            domain.status === "active"
              ? "bg-live-dim text-live"
              : "bg-ground-overlay text-ink-faint"
          }`}
        >
          {domain.status}
        </span>
      </div>

      <div className="mt-8 grid grid-cols-2 gap-6 md:grid-cols-4">
        <Field label="Registered" value={fmt(domain.registration_date)} />
        <Field label="Expires" value={fmt(domain.expiry_date)} />
        <Field label="Auto-renew" value={domain.auto_renew ? "on" : "off"} />
        <Field label="Privacy" value={domain.privacy_enabled ? "on" : "off"} />
        <Field label="Locked" value={domain.locked ? "yes" : "no"} />
        <Field
          label="Nameservers"
          value={domain.nameservers?.replace(/,/g, "\n") || "none"}
          mono
        />
      </div>

      <section className="mt-12">
        <h2 className="text-sm font-medium text-ink">DNS records</h2>
        {zone && zone.records.length > 0 ? (
          <div className="mt-4 overflow-hidden rounded-lg border border-edge">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-edge bg-ground-raised text-xs text-ink-faint">
                  <th className="px-4 py-2 font-medium">Type</th>
                  <th className="px-4 py-2 font-medium">Name</th>
                  <th className="px-4 py-2 font-medium">Content</th>
                  <th className="px-4 py-2 font-medium text-right">TTL</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-edge font-mono text-xs">
                {zone.records.map((r) => (
                  <tr key={r.id} className="hover:bg-ground-raised/50">
                    <td className="px-4 py-2 text-focus">{r.record_type}</td>
                    <td className="px-4 py-2 text-ink">{r.name}</td>
                    <td className="px-4 py-2 text-ink-dim">{r.content}</td>
                    <td className="px-4 py-2 text-right text-ink-faint">
                      {r.ttl}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="mt-4 text-sm text-ink-faint">
            No DNS records. Add one or apply a template.
          </p>
        )}
      </section>
    </div>
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
      <p
        className={`mt-1 text-sm text-ink whitespace-pre-line ${mono ? "font-mono" : ""}`}
      >
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

function Loading() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <p className="text-sm text-ink-faint">Loading...</p>
    </div>
  );
}

function NotFound() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <p className="text-sm text-ink-faint">Domain not found.</p>
    </div>
  );
}
