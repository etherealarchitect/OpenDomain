"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/shell";
import { api, type ContactResponse } from "@/lib/api";
import { toast } from "@/components/ui/toast";

export default function TransferPage() {
  const router = useRouter();
  const [domain, setDomain] = useState("");
  const [authCode, setAuthCode] = useState("");
  const [contacts, setContacts] = useState<ContactResponse[]>([]);
  const [contactId, setContactId] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api
      .listContacts()
      .then((data) => {
        setContacts(data);
        if (data.length > 0) setContactId(data[0].id);
      })
      .catch(() => toast("Failed to load contacts", "error"))
      .finally(() => setLoading(false));
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!domain.trim() || !authCode.trim() || !contactId) {
      toast("All fields are required", "error");
      return;
    }
    setSubmitting(true);
    try {
      await api.transferDomainIn({
        domain: domain.trim().toLowerCase(),
        auth_code: authCode.trim(),
        registrant_contact_id: contactId,
      });
      toast(`Transfer initiated for ${domain}`, "success");
      router.push("/domains");
    } catch (e) {
      toast(
        e instanceof Error ? e.message : "Transfer failed",
        "error",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Shell>
      <div className="mx-auto max-w-xl px-6 py-8">
        <h1 className="text-xl font-semibold text-ink">Transfer Domain In</h1>
        <p className="mt-1 text-sm text-ink-dim">
          Transfer an existing domain from another registrar.
        </p>

        {loading ? (
          <p className="mt-8 text-sm text-ink-faint">Loading...</p>
        ) : (
          <form onSubmit={handleSubmit} className="mt-8 space-y-6">
            <label className="block">
              <span className="text-xs text-ink-dim">
                Domain name <span className="text-fault/60">*</span>
              </span>
              <input
                type="text"
                required
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                placeholder="example.com"
                className="mt-1 block w-full rounded-md border border-edge bg-ground-raised px-3 py-2 font-mono text-sm text-ink placeholder:text-ink-faint focus:border-focus focus:outline-none focus:ring-1 focus:ring-focus"
              />
            </label>

            <label className="block">
              <span className="text-xs text-ink-dim">
                Authorization code (EPP auth code){" "}
                <span className="text-fault/60">*</span>
              </span>
              <input
                type="text"
                required
                value={authCode}
                onChange={(e) => setAuthCode(e.target.value)}
                placeholder="Provided by your current registrar"
                className="mt-1 block w-full rounded-md border border-edge bg-ground-raised px-3 py-2 font-mono text-sm text-ink placeholder:text-ink-faint focus:border-focus focus:outline-none focus:ring-1 focus:ring-focus"
              />
              <p className="mt-1 text-xs text-ink-faint">
                Get this from your current registrar&apos;s control panel.
              </p>
            </label>

            <div>
              <span className="text-xs text-ink-dim">
                Registrant contact <span className="text-fault/60">*</span>
              </span>
              {contacts.length === 0 ? (
                <div className="mt-2 rounded-lg border border-edge bg-ground-raised p-4 text-center">
                  <p className="text-sm text-ink-dim">No contacts found.</p>
                  <a
                    href="/contacts"
                    className="mt-1 inline-block text-sm text-focus hover:underline"
                  >
                    Create a contact first
                  </a>
                </div>
              ) : (
                <div className="mt-2 space-y-2">
                  {contacts.map((c) => (
                    <button
                      key={c.id}
                      type="button"
                      onClick={() => setContactId(c.id)}
                      className={`w-full rounded-lg border p-3 text-left transition-colors ${
                        contactId === c.id
                          ? "border-focus bg-focus/5"
                          : "border-edge bg-ground-raised hover:border-ink-faint"
                      }`}
                    >
                      <p className="text-sm font-medium text-ink">
                        {c.first_name} {c.last_name}
                      </p>
                      <p className="text-xs text-ink-faint">
                        {c.label} &middot; {c.email}
                      </p>
                    </button>
                  ))}
                </div>
              )}
            </div>

            <button
              type="submit"
              disabled={submitting || !contactId}
              className="rounded-md bg-focus px-4 py-2 text-sm font-medium text-ground transition-colors hover:bg-focus/90 disabled:opacity-50"
            >
              {submitting ? "Initiating transfer..." : "Start Transfer"}
            </button>
          </form>
        )}
      </div>
    </Shell>
  );
}
