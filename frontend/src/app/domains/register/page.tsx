"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { Shell } from "@/components/layout/shell";
import {
  api,
  type ContactResponse,
  type DomainSearchResult,
} from "@/lib/api";
import { toast } from "@/components/ui/toast";

function RegisterContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const domainParam = searchParams.get("domain") || "";

  const [step, setStep] = useState(1);
  const [domain, setDomain] = useState(domainParam);
  const [searchResult, setSearchResult] = useState<DomainSearchResult | null>(
    null,
  );
  const [contacts, setContacts] = useState<ContactResponse[]>([]);
  const [contactId, setContactId] = useState("");
  const [years, setYears] = useState(1);
  const [privacy, setPrivacy] = useState(true);
  const [autoRenew, setAutoRenew] = useState(true);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    Promise.all([
      domainParam
        ? api.searchDomains(domainParam).catch(() => [] as DomainSearchResult[])
        : Promise.resolve([] as DomainSearchResult[]),
      api.listContacts().catch(() => [] as ContactResponse[]),
    ]).then(([results, ctcts]) => {
      const match = results.find(
        (r) => r.domain === domainParam && r.available,
      );
      if (match) setSearchResult(match);
      setContacts(ctcts);
      if (ctcts.length > 0) setContactId(ctcts[0].id);
      setLoading(false);
    });
  }, [domainParam]);

  async function handleRegister() {
    if (!contactId) {
      toast("Please select a contact", "error");
      return;
    }
    setSubmitting(true);
    try {
      const res = await api.registerDomain({
        domain,
        period_years: years,
        registrant_contact_id: contactId,
        privacy_enabled: privacy,
        auto_renew: autoRenew,
      });
      toast(`${domain} registered successfully!`, "success");
      router.push(`/domains/${res.id}`);
    } catch (e) {
      toast(e instanceof Error ? e.message : "Registration failed", "error");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <Shell>
        <div className="mx-auto max-w-2xl px-6 py-8">
          <p className="text-sm text-ink-faint">Loading...</p>
        </div>
      </Shell>
    );
  }

  const priceCents = searchResult?.price_cents || 0;
  const totalCents = priceCents * years;

  return (
    <Shell>
      <div className="mx-auto max-w-2xl px-6 py-8">
        <h1 className="text-xl font-semibold text-ink">Register Domain</h1>

        <div className="mt-6 flex gap-2">
          {[1, 2, 3].map((s) => (
            <div
              key={s}
              className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-medium ${
                s === step
                  ? "bg-focus text-ground"
                  : s < step
                    ? "bg-live-dim text-live"
                    : "bg-ground-raised text-ink-faint"
              }`}
            >
              {s}
            </div>
          ))}
        </div>

        {step === 1 && (
          <div className="mt-8">
            <h2 className="text-sm font-medium text-ink">
              Domain &amp; Registration Period
            </h2>
            <div className="mt-4 rounded-lg border border-edge bg-ground-raised p-5">
              <div className="flex items-center justify-between">
                <span className="font-mono text-sm text-ink">{domain}</span>
                {searchResult ? (
                  <span className="rounded-full bg-live-dim px-2 py-0.5 text-xs font-medium text-live">
                    Available
                  </span>
                ) : (
                  <span className="text-xs text-ink-faint">
                    Availability unknown
                  </span>
                )}
              </div>
              {priceCents > 0 && (
                <p className="mt-2 font-mono text-xs text-ink-dim">
                  ${(priceCents / 100).toFixed(2)}/yr
                </p>
              )}
            </div>

            <label className="mt-6 block">
              <span className="text-xs text-ink-dim">
                Registration period (years)
              </span>
              <select
                value={years}
                onChange={(e) => setYears(Number(e.target.value))}
                className="mt-1 block w-32 rounded-md border border-edge bg-ground px-3 py-1.5 text-sm text-ink focus:border-focus focus:outline-none focus:ring-1 focus:ring-focus"
              >
                {[1, 2, 3, 5, 10].map((y) => (
                  <option key={y} value={y}>
                    {y} year{y > 1 ? "s" : ""}
                  </option>
                ))}
              </select>
            </label>

            <div className="mt-6 flex items-center gap-6">
              <Toggle
                label="WHOIS Privacy"
                checked={privacy}
                onChange={setPrivacy}
              />
              <Toggle
                label="Auto-renew"
                checked={autoRenew}
                onChange={setAutoRenew}
              />
            </div>

            <button
              onClick={() => setStep(2)}
              className="mt-8 rounded-md bg-focus px-4 py-2 text-sm font-medium text-ground transition-colors hover:bg-focus/90"
            >
              Next: Select Contact
            </button>
          </div>
        )}

        {step === 2 && (
          <div className="mt-8">
            <h2 className="text-sm font-medium text-ink">
              Registrant Contact
            </h2>
            {contacts.length === 0 ? (
              <div className="mt-4 rounded-lg border border-edge bg-ground-raised p-6 text-center">
                <p className="text-sm text-ink-dim">No contacts found.</p>
                <a
                  href="/contacts"
                  className="mt-2 inline-block text-sm text-focus hover:underline"
                >
                  Create a contact first
                </a>
              </div>
            ) : (
              <div className="mt-4 space-y-2">
                {contacts.map((c) => (
                  <button
                    key={c.id}
                    onClick={() => setContactId(c.id)}
                    className={`w-full rounded-lg border p-4 text-left transition-colors ${
                      contactId === c.id
                        ? "border-focus bg-focus/5"
                        : "border-edge bg-ground-raised hover:border-ink-faint"
                    }`}
                  >
                    <p className="text-sm font-medium text-ink">
                      {c.first_name} {c.last_name}
                    </p>
                    <p className="mt-0.5 text-xs text-ink-faint">
                      {c.label} &middot; {c.email}
                    </p>
                  </button>
                ))}
              </div>
            )}
            <div className="mt-8 flex gap-2">
              <button
                onClick={() => setStep(1)}
                className="rounded-md border border-edge px-4 py-2 text-sm text-ink-dim transition-colors hover:bg-ground-overlay"
              >
                Back
              </button>
              <button
                onClick={() => setStep(3)}
                disabled={!contactId}
                className="rounded-md bg-focus px-4 py-2 text-sm font-medium text-ground transition-colors hover:bg-focus/90 disabled:opacity-50"
              >
                Next: Review
              </button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="mt-8">
            <h2 className="text-sm font-medium text-ink">
              Review &amp; Confirm
            </h2>
            <div className="mt-4 rounded-lg border border-edge bg-ground-raised p-5">
              <dl className="space-y-3 text-sm">
                <Row label="Domain" value={domain} mono />
                <Row label="Period" value={`${years} year${years > 1 ? "s" : ""}`} />
                <Row
                  label="Contact"
                  value={
                    contacts.find((c) => c.id === contactId)
                      ? `${contacts.find((c) => c.id === contactId)!.first_name} ${contacts.find((c) => c.id === contactId)!.last_name}`
                      : "—"
                  }
                />
                <Row
                  label="WHOIS Privacy"
                  value={privacy ? "Enabled" : "Disabled"}
                />
                <Row
                  label="Auto-renew"
                  value={autoRenew ? "Enabled" : "Disabled"}
                />
                {totalCents > 0 && (
                  <Row
                    label="Total"
                    value={`$${(totalCents / 100).toFixed(2)}`}
                    mono
                  />
                )}
              </dl>
            </div>
            <div className="mt-8 flex gap-2">
              <button
                onClick={() => setStep(2)}
                className="rounded-md border border-edge px-4 py-2 text-sm text-ink-dim transition-colors hover:bg-ground-overlay"
              >
                Back
              </button>
              <button
                onClick={handleRegister}
                disabled={submitting}
                className="rounded-md bg-focus px-4 py-2 text-sm font-medium text-ground transition-colors hover:bg-focus/90 disabled:opacity-50"
              >
                {submitting ? "Registering..." : "Register Domain"}
              </button>
            </div>
          </div>
        )}
      </div>
    </Shell>
  );
}

function Row({
  label,
  value,
  mono,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div className="flex justify-between">
      <dt className="text-ink-dim">{label}</dt>
      <dd className={`text-ink ${mono ? "font-mono" : ""}`}>{value}</dd>
    </div>
  );
}

function Toggle({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <label className="flex items-center gap-2 text-xs text-ink-dim">
      <button
        type="button"
        onClick={() => onChange(!checked)}
        className={`relative h-5 w-9 rounded-full transition-colors ${
          checked ? "bg-live" : "bg-edge"
        }`}
      >
        <span
          className={`absolute top-0.5 left-0.5 h-4 w-4 rounded-full bg-white transition-transform ${
            checked ? "translate-x-4" : "translate-x-0"
          }`}
        />
      </button>
      {label}
    </label>
  );
}

export default function RegisterPage() {
  return (
    <Suspense>
      <RegisterContent />
    </Suspense>
  );
}
