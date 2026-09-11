"use client";

import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/shell";
import {
  api,
  type InvoiceResponse,
  type TransactionResponse,
  type PaymentMethodResponse,
} from "@/lib/api";
import { toast } from "@/components/ui/toast";

type Tab = "invoices" | "transactions" | "payment";

export default function BillingPage() {
  const [tab, setTab] = useState<Tab>("invoices");
  const [invoices, setInvoices] = useState<InvoiceResponse[]>([]);
  const [transactions, setTransactions] = useState<TransactionResponse[]>([]);
  const [methods, setMethods] = useState<PaymentMethodResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.listInvoices().catch(() => []),
      api.listTransactions().catch(() => []),
      api.listPaymentMethods().catch(() => []),
    ]).then(([i, t, m]) => {
      setInvoices(i);
      setTransactions(t);
      setMethods(m);
      setLoading(false);
    });
  }, []);

  const TABS: { key: Tab; label: string }[] = [
    { key: "invoices", label: "Invoices" },
    { key: "transactions", label: "Transactions" },
    { key: "payment", label: "Payment Methods" },
  ];

  return (
    <Shell>
      <div className="mx-auto max-w-4xl px-6 py-8">
        <h1 className="text-xl font-semibold text-ink">Billing</h1>

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
            {tab === "invoices" && (
              invoices.length === 0 ? (
                <Empty text="No invoices yet." />
              ) : (
                <div className="overflow-hidden rounded-lg border border-edge">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-edge bg-ground-raised text-xs text-ink-faint">
                        <th className="px-4 py-2.5 font-medium">Invoice</th>
                        <th className="px-4 py-2.5 font-medium">Status</th>
                        <th className="px-4 py-2.5 font-medium">Total</th>
                        <th className="px-4 py-2.5 font-medium">Date</th>
                        <th className="px-4 py-2.5 font-medium text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-edge">
                      {invoices.map((inv) => (
                        <tr key={inv.id} className="hover:bg-ground-raised/50">
                          <td className="px-4 py-3 font-mono text-xs text-ink">{inv.invoice_number}</td>
                          <td className="px-4 py-3">
                            <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                              inv.status === "paid" ? "bg-live-dim text-live" :
                              inv.status === "pending" ? "bg-caution/10 text-caution" :
                              "bg-ground-overlay text-ink-faint"
                            }`}>
                              {inv.status}
                            </span>
                          </td>
                          <td className="px-4 py-3 font-mono text-sm text-ink">
                            ${(inv.total_cents / 100).toFixed(2)} {inv.currency}
                          </td>
                          <td className="px-4 py-3 text-xs text-ink-dim">
                            {new Date(inv.created_at).toLocaleDateString("en-AU")}
                          </td>
                          <td className="px-4 py-3 text-right">
                            {inv.status === "pending" && (
                              <button className="text-xs text-focus hover:underline">Pay</button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )
            )}

            {tab === "transactions" && (
              transactions.length === 0 ? (
                <Empty text="No transactions yet." />
              ) : (
                <div className="overflow-hidden rounded-lg border border-edge">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-edge bg-ground-raised text-xs text-ink-faint">
                        <th className="px-4 py-2.5 font-medium">Type</th>
                        <th className="px-4 py-2.5 font-medium">Description</th>
                        <th className="px-4 py-2.5 font-medium">Amount</th>
                        <th className="px-4 py-2.5 font-medium">Date</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-edge">
                      {transactions.map((tx) => (
                        <tr key={tx.id} className="hover:bg-ground-raised/50">
                          <td className="px-4 py-3">
                            <span className="rounded-full bg-ground-overlay px-2 py-0.5 text-xs font-medium text-ink-dim">
                              {tx.transaction_type}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-sm text-ink">{tx.description}</td>
                          <td className="px-4 py-3 font-mono text-sm text-ink">
                            ${(tx.amount_cents / 100).toFixed(2)} {tx.currency}
                          </td>
                          <td className="px-4 py-3 text-xs text-ink-dim">
                            {new Date(tx.created_at).toLocaleDateString("en-AU")}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )
            )}

            {tab === "payment" && (
              <div className="space-y-3">
                {methods.length === 0 ? (
                  <Empty text="No payment methods on file." />
                ) : (
                  methods.map((m) => (
                    <div key={m.id} className="flex items-center justify-between rounded-lg border border-edge bg-ground-raised p-4">
                      <div>
                        <p className="text-sm font-medium text-ink">{m.label}</p>
                        <p className="mt-0.5 text-xs text-ink-faint">
                          {m.method_type}{m.last_four ? ` ending in ${m.last_four}` : ""}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        {m.is_default && (
                          <span className="rounded-full bg-focus-dim px-2 py-0.5 text-xs font-medium text-focus">
                            Default
                          </span>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
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
