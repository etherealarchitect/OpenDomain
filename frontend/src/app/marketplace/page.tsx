"use client";

import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/shell";
import {
  api,
  type MarketplaceListingResponse,
  type DomainResponse,
} from "@/lib/api";
import { toast } from "@/components/ui/toast";

type View = "browse" | "mine";

export default function MarketplacePage() {
  const [view, setView] = useState<View>("browse");
  const [listings, setListings] = useState<MarketplaceListingResponse[]>([]);
  const [myDomains, setMyDomains] = useState<DomainResponse[]>([]);
  const [loading, setLoading] = useState(true);

  const [showCreate, setShowCreate] = useState(false);
  const [selectedDomain, setSelectedDomain] = useState("");
  const [price, setPrice] = useState("");
  const [description, setDescription] = useState("");
  const [creating, setCreating] = useState(false);

  const [offerListingId, setOfferListingId] = useState<string | null>(null);
  const [offerAmount, setOfferAmount] = useState("");
  const [offerMessage, setOfferMessage] = useState("");

  useEffect(() => {
    Promise.all([
      api.listMarketplaceListings().catch(() => []),
      api.listDomains().catch(() => []),
    ]).then(([l, d]) => {
      setListings(l);
      setMyDomains(d);
      setLoading(false);
    });
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedDomain || !price) return;
    setCreating(true);
    try {
      const listing = await api.createListing(
        selectedDomain,
        Math.round(parseFloat(price) * 100),
        description || undefined,
      );
      setListings((prev) => [listing, ...prev]);
      setShowCreate(false);
      setSelectedDomain("");
      setPrice("");
      setDescription("");
      toast("Domain listed for sale", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed", "error");
    } finally {
      setCreating(false);
    }
  }

  async function handleOffer(e: React.FormEvent) {
    e.preventDefault();
    if (!offerListingId || !offerAmount) return;
    try {
      await api.createOffer(
        offerListingId,
        Math.round(parseFloat(offerAmount) * 100),
        offerMessage || undefined,
      );
      toast("Offer submitted", "success");
      setOfferListingId(null);
      setOfferAmount("");
      setOfferMessage("");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed", "error");
    }
  }

  return (
    <Shell>
      <div className="mx-auto max-w-4xl px-6 py-8">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-ink">Marketplace</h1>
          <button
            onClick={() => setShowCreate(true)}
            className="rounded-md bg-focus px-3 py-1.5 text-sm font-medium text-ground transition-colors hover:bg-focus/90"
          >
            List a domain
          </button>
        </div>

        <div className="mt-6 flex gap-1 rounded-md border border-edge bg-ground-raised p-0.5">
          {(["browse", "mine"] as View[]).map((v) => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`rounded px-3 py-1.5 text-xs transition-colors ${
                view === v ? "bg-ground-overlay text-ink" : "text-ink-faint hover:text-ink-dim"
              }`}
            >
              {v === "browse" ? "Browse" : "My Listings"}
            </button>
          ))}
        </div>

        {showCreate && (
          <form onSubmit={handleCreate} className="mt-6 rounded-lg border border-edge bg-ground-raised p-5">
            <h2 className="text-sm font-medium text-ink">List domain for sale</h2>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <label className="flex flex-col gap-1">
                <span className="text-xs text-ink-dim">Domain</span>
                <select
                  value={selectedDomain}
                  onChange={(e) => setSelectedDomain(e.target.value)}
                  required
                  className="rounded-md border border-edge bg-ground px-3 py-1.5 text-sm text-ink focus:border-focus focus:outline-none focus:ring-1 focus:ring-focus"
                >
                  <option value="">Select domain</option>
                  {myDomains.filter((d) => d.status === "active").map((d) => (
                    <option key={d.id} value={d.id}>{d.name}</option>
                  ))}
                </select>
              </label>
              <label className="flex flex-col gap-1">
                <span className="text-xs text-ink-dim">Asking price (USD)</span>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  required
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  placeholder="99.00"
                  className="rounded-md border border-edge bg-ground px-3 py-1.5 text-sm text-ink placeholder:text-ink-faint focus:border-focus focus:outline-none focus:ring-1 focus:ring-focus"
                />
              </label>
              <label className="flex flex-col gap-1 sm:col-span-2">
                <span className="text-xs text-ink-dim">Description</span>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={2}
                  className="rounded-md border border-edge bg-ground px-3 py-1.5 text-sm text-ink placeholder:text-ink-faint focus:border-focus focus:outline-none focus:ring-1 focus:ring-focus"
                />
              </label>
            </div>
            <div className="mt-4 flex gap-2">
              <button type="submit" disabled={creating} className="rounded-md bg-focus px-4 py-2 text-sm font-medium text-ground transition-colors hover:bg-focus/90 disabled:opacity-50">
                {creating ? "Listing..." : "Create Listing"}
              </button>
              <button type="button" onClick={() => setShowCreate(false)} className="rounded-md border border-edge px-4 py-2 text-sm text-ink-dim transition-colors hover:bg-ground-overlay">
                Cancel
              </button>
            </div>
          </form>
        )}

        {loading ? (
          <p className="mt-8 text-sm text-ink-faint">Loading...</p>
        ) : listings.length === 0 ? (
          <div className="mt-8 rounded-lg border border-edge bg-ground-raised p-8 text-center">
            <p className="text-sm text-ink-dim">No listings yet.</p>
          </div>
        ) : (
          <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {listings.map((l) => (
              <div key={l.id} className="rounded-lg border border-edge bg-ground-raised p-4">
                <p className="font-mono text-sm font-medium text-ink">{l.domain_name || `Domain ${l.domain_id.slice(0, 8)}`}</p>
                <p className="mt-1 text-lg font-semibold text-ink">${(l.asking_price_cents / 100).toFixed(2)}</p>
                {l.description && (
                  <p className="mt-1 text-xs text-ink-dim line-clamp-2">{l.description}</p>
                )}
                <div className="mt-3 flex items-center justify-between">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    l.status === "active" ? "bg-live-dim text-live" : "bg-ground-overlay text-ink-faint"
                  }`}>
                    {l.status}
                  </span>
                  {l.status === "active" && (
                    <button
                      onClick={() => { setOfferListingId(l.id); setOfferAmount(""); }}
                      className="text-xs text-focus hover:underline"
                    >
                      Make offer
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {offerListingId && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-ground/80">
            <form onSubmit={handleOffer} className="w-full max-w-md rounded-lg border border-edge bg-ground-raised p-6 shadow-lg">
              <h2 className="text-sm font-medium text-ink">Make an offer</h2>
              <label className="mt-4 flex flex-col gap-1">
                <span className="text-xs text-ink-dim">Amount (USD)</span>
                <input type="number" step="0.01" min="0" required value={offerAmount} onChange={(e) => setOfferAmount(e.target.value)} className="rounded-md border border-edge bg-ground px-3 py-1.5 text-sm text-ink focus:border-focus focus:outline-none focus:ring-1 focus:ring-focus" />
              </label>
              <label className="mt-3 flex flex-col gap-1">
                <span className="text-xs text-ink-dim">Message (optional)</span>
                <textarea value={offerMessage} onChange={(e) => setOfferMessage(e.target.value)} rows={2} className="rounded-md border border-edge bg-ground px-3 py-1.5 text-sm text-ink focus:border-focus focus:outline-none focus:ring-1 focus:ring-focus" />
              </label>
              <div className="mt-4 flex gap-2">
                <button type="submit" className="rounded-md bg-focus px-4 py-2 text-sm font-medium text-ground transition-colors hover:bg-focus/90">Submit Offer</button>
                <button type="button" onClick={() => setOfferListingId(null)} className="rounded-md border border-edge px-4 py-2 text-sm text-ink-dim transition-colors hover:bg-ground-overlay">Cancel</button>
              </div>
            </form>
          </div>
        )}
      </div>
    </Shell>
  );
}
