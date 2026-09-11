"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { AuthLayout } from "@/components/ui/auth-layout";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const challenge = await login(email, password);
      const destination = challenge.next_step === "mfa_enrollment" ? "/mfa/setup" : "/mfa/challenge";
      router.push(`${destination}?challenge=${encodeURIComponent(challenge.challenge_id)}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "We could not sign you in. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout
      eyebrow="Secure sign in"
      title="Welcome back"
      description="Sign in with your password, then confirm your identity with your authenticator app."
      footer={<>New to OpenDomain? <Link href="/register" className="font-medium text-focus hover:underline">Create an account</Link></>}
    >
      <form onSubmit={handleSubmit} className="mt-7 space-y-4" noValidate>
        {error && <div role="alert" className="rounded-lg border border-fault/30 bg-fault/10 px-3 py-2.5 text-sm text-fault">{error}</div>}
        <label className="block">
          <span className="text-xs font-medium text-ink-dim">Email address</span>
          <input autoComplete="email" type="email" required value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" className="mt-1.5 w-full rounded-lg border border-edge bg-ground px-3 py-2.5 text-sm text-ink outline-none transition focus:border-focus focus:ring-2 focus:ring-focus/20" />
        </label>
        <label className="block">
          <span className="flex items-center justify-between text-xs font-medium text-ink-dim">Password <Link href="/forgot-password" className="font-normal text-focus hover:underline">Forgot password?</Link></span>
          <input autoComplete="current-password" type="password" required value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Your password" className="mt-1.5 w-full rounded-lg border border-edge bg-ground px-3 py-2.5 text-sm text-ink outline-none transition focus:border-focus focus:ring-2 focus:ring-focus/20" />
        </label>
        <button disabled={loading} type="submit" className="mt-2 w-full rounded-lg bg-focus px-4 py-3 text-sm font-semibold text-ground transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60">
          {loading ? "Verifying password…" : "Continue"}
        </button>
      </form>
    </AuthLayout>
  );
}
