"use client";

import { Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AuthLayout, PasswordStrength } from "@/components/ui/auth-layout";
import { api } from "@/lib/api";

export default function ResetPasswordPage() {
  return <Suspense fallback={<AuthPageLoading />}><ResetPasswordContent /></Suspense>;
}

function ResetPasswordContent() {
  const queryToken = useSearchParams().get("token");
  const [token, setToken] = useState(queryToken);
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const valid = password.length >= 12 && /[a-z]/.test(password) && /[A-Z]/.test(password) && /\d/.test(password);

  useEffect(() => {
    if (!queryToken && window.location.hash.startsWith("#token=")) {
      setToken(decodeURIComponent(window.location.hash.slice("#token=".length)));
    }
  }, [queryToken]);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!token || password !== confirm || !valid) { setError(password !== confirm ? "Your passwords do not match." : "Choose a password that meets every requirement."); return; }
    setLoading(true); setError("");
    try { await api.resetPassword(token, password); router.replace("/login"); } catch (err) { setError(err instanceof Error ? err.message : "We could not reset this password."); } finally { setLoading(false); }
  }

  return <AuthLayout eyebrow="New password" title="Secure your account" description="Choose a new, unique password. This signs out any active sessions." footer={<Link href="/login" className="font-medium text-focus hover:underline">Return to sign in</Link>}>
    <form onSubmit={submit} className="mt-7 space-y-4">{error && <div role="alert" className="rounded-lg border border-fault/30 bg-fault/10 px-3 py-2.5 text-sm text-fault">{error}</div>}<label className="block"><span className="text-xs font-medium text-ink-dim">New password</span><input autoComplete="new-password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required className="mt-1.5 w-full rounded-lg border border-edge bg-ground px-3 py-2.5 text-sm text-ink outline-none transition focus:border-focus focus:ring-2 focus:ring-focus/20" /><PasswordStrength password={password} /></label><label className="block"><span className="text-xs font-medium text-ink-dim">Confirm password</span><input autoComplete="new-password" type="password" value={confirm} onChange={(event) => setConfirm(event.target.value)} required className="mt-1.5 w-full rounded-lg border border-edge bg-ground px-3 py-2.5 text-sm text-ink outline-none transition focus:border-focus focus:ring-2 focus:ring-focus/20" /></label><button disabled={loading || !token} className="w-full rounded-lg bg-focus px-4 py-3 text-sm font-semibold text-ground disabled:opacity-60">{loading ? "Resetting password…" : "Reset password"}</button></form>
  </AuthLayout>;
}

function AuthPageLoading() {
  return <div className="min-h-screen bg-ground" />;
}
