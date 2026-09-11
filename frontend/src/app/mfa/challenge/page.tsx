"use client";

import { Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { AuthLayout } from "@/components/ui/auth-layout";
import { useAuth } from "@/lib/auth";

export default function MfaChallengePage() {
  return <Suspense fallback={<AuthPageLoading />}><MfaChallengeContent /></Suspense>;
}

function MfaChallengeContent() {
  const challenge = useSearchParams().get("challenge");
  const router = useRouter();
  const { completeMfa } = useAuth();
  const [code, setCode] = useState("");
  const [error, setError] = useState(challenge ? "" : "Your sign-in session is missing or expired.");
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!challenge) return;
    setError("");
    setLoading(true);
    try {
      await completeMfa(challenge, code);
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "That authentication code is not valid.");
    } finally {
      setLoading(false);
    }
  }

  return <AuthLayout eyebrow="Second factor" title="Confirm it’s you" description="Enter the current code from your authenticator app, or use one of your recovery codes." footer={<Link href="/login" className="font-medium text-focus hover:underline">Use another account</Link>}>
    <form onSubmit={submit} className="mt-7 space-y-4">
      {error && <div role="alert" className="rounded-lg border border-fault/30 bg-fault/10 px-3 py-2.5 text-sm text-fault">{error}</div>}
      <label className="block"><span className="text-xs font-medium text-ink-dim">Authenticator or recovery code</span><input autoFocus autoComplete="one-time-code" value={code} onChange={(event) => setCode(event.target.value.replace(/\s/g, "").toUpperCase())} required placeholder="000000 or A1B2C3D4" className="mt-1.5 w-full rounded-lg border border-edge bg-ground px-3 py-3 font-mono text-base tracking-[0.16em] text-ink outline-none transition focus:border-focus focus:ring-2 focus:ring-focus/20" /></label>
      <button disabled={loading || code.length < 6} type="submit" className="w-full rounded-lg bg-focus px-4 py-3 text-sm font-semibold text-ground transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60">{loading ? "Confirming…" : "Sign in securely"}</button>
    </form>
  </AuthLayout>;
}

function AuthPageLoading() {
  return <div className="min-h-screen bg-ground" />;
}
