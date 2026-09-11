"use client";

import Link from "next/link";
import { useState } from "react";
import { AuthLayout } from "@/components/ui/auth-layout";
import { api } from "@/lib/api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [done, setDone] = useState(false);
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    try { await api.forgotPassword(email); } finally { setDone(true); setLoading(false); }
  }

  return <AuthLayout eyebrow="Account recovery" title="Reset your password" description="Enter your email and we’ll send recovery instructions if an eligible account exists." footer={<Link href="/login" className="font-medium text-focus hover:underline">Return to sign in</Link>}>
    {done ? <div className="mt-7 rounded-xl border border-live/30 bg-live/10 p-4 text-sm leading-6 text-ink-dim">If an eligible account exists, an email has been sent. Check your inbox and spam folder for the recovery link.</div> : <form onSubmit={submit} className="mt-7 space-y-4"><label className="block"><span className="text-xs font-medium text-ink-dim">Email address</span><input type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" className="mt-1.5 w-full rounded-lg border border-edge bg-ground px-3 py-2.5 text-sm text-ink outline-none transition focus:border-focus focus:ring-2 focus:ring-focus/20" /></label><button disabled={loading} className="w-full rounded-lg bg-focus px-4 py-3 text-sm font-semibold text-ground disabled:opacity-60">{loading ? "Sending…" : "Send recovery link"}</button></form>}
  </AuthLayout>;
}
