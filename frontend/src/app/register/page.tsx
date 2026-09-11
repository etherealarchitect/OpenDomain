"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { AuthLayout, PasswordStrength } from "@/components/ui/auth-layout";
import { useAuth } from "@/lib/auth";

export default function RegisterPage() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const router = useRouter();

  const passwordValid = password.length >= 12 && /[a-z]/.test(password) && /[A-Z]/.test(password) && /\d/.test(password);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    if (password !== confirm) return setError("Your passwords do not match.");
    if (!passwordValid) return setError("Use a stronger password that meets every requirement.");
    setLoading(true);
    try {
      await register(email, password, fullName);
      router.push(`/verify-email/pending?email=${encodeURIComponent(email.trim().toLowerCase())}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "We could not create your account. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout
      eyebrow="Start securely"
      title="Create your account"
      description="Set up your OpenDomain account. We’ll verify your email first, then protect it with your authenticator app."
      footer={<>Already have an account? <Link href="/login" className="font-medium text-focus hover:underline">Sign in</Link></>}
    >
      <form onSubmit={handleSubmit} className="mt-7 space-y-4" noValidate>
        {error && <div role="alert" className="rounded-lg border border-fault/30 bg-fault/10 px-3 py-2.5 text-sm text-fault">{error}</div>}
        <label className="block">
          <span className="text-xs font-medium text-ink-dim">Full name</span>
          <input autoComplete="name" value={fullName} onChange={(e) => setFullName(e.target.value)} required minLength={2} placeholder="Alex Morgan" className="mt-1.5 w-full rounded-lg border border-edge bg-ground px-3 py-2.5 text-sm text-ink outline-none transition focus:border-focus focus:ring-2 focus:ring-focus/20" />
        </label>
        <label className="block">
          <span className="text-xs font-medium text-ink-dim">Email address</span>
          <input autoComplete="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required placeholder="you@example.com" className="mt-1.5 w-full rounded-lg border border-edge bg-ground px-3 py-2.5 text-sm text-ink outline-none transition focus:border-focus focus:ring-2 focus:ring-focus/20" />
        </label>
        <label className="block">
          <span className="text-xs font-medium text-ink-dim">Password</span>
          <input autoComplete="new-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required placeholder="Create a strong password" className="mt-1.5 w-full rounded-lg border border-edge bg-ground px-3 py-2.5 text-sm text-ink outline-none transition focus:border-focus focus:ring-2 focus:ring-focus/20" />
          <PasswordStrength password={password} />
        </label>
        <label className="block">
          <span className="text-xs font-medium text-ink-dim">Confirm password</span>
          <input autoComplete="new-password" type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required placeholder="Repeat your password" className="mt-1.5 w-full rounded-lg border border-edge bg-ground px-3 py-2.5 text-sm text-ink outline-none transition focus:border-focus focus:ring-2 focus:ring-focus/20" />
        </label>
        <button disabled={loading} type="submit" className="mt-2 w-full rounded-lg bg-focus px-4 py-3 text-sm font-semibold text-ground transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60">
          {loading ? "Creating secure account…" : "Continue to email verification"}
        </button>
      </form>
      <p className="mt-5 text-center text-[11px] leading-5 text-ink-faint">By continuing, you agree to secure account verification and required multi-factor authentication.</p>
    </AuthLayout>
  );
}
