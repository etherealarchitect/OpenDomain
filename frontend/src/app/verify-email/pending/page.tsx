"use client";

import { Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useState } from "react";
import { AuthLayout } from "@/components/ui/auth-layout";
import { api } from "@/lib/api";

export default function VerifyEmailPendingPage() {
  return <Suspense fallback={<AuthPageLoading />}><VerifyEmailPendingContent /></Suspense>;
}

function VerifyEmailPendingContent() {
  const searchParams = useSearchParams();
  const email = searchParams.get("email") ?? "your email address";
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  async function resend() {
    if (email === "your email address") return;
    setLoading(true);
    try {
      await api.resendVerification(email);
    } finally {
      setSent(true);
      setLoading(false);
    }
  }

  return (
    <AuthLayout eyebrow="One more step" title="Verify your email" description={`We sent a secure verification link to ${email}. Open it in this browser to continue with authenticator setup.`} footer={<>Wrong email? <Link href="/register" className="font-medium text-focus hover:underline">Create a new account</Link></>}>
      <div className="mt-7 rounded-xl border border-edge bg-ground p-4">
        <p className="font-mono text-xs text-live">01 / EMAIL VERIFICATION</p>
        <p className="mt-2 text-sm leading-6 text-ink-dim">Links expire for your protection. If you can’t find the message, check your spam folder or request another one.</p>
      </div>
      <button onClick={resend} disabled={loading || sent || email === "your email address"} className="mt-5 w-full rounded-lg border border-edge px-4 py-3 text-sm font-medium text-ink transition hover:border-focus hover:text-focus disabled:cursor-not-allowed disabled:opacity-60">
        {sent ? "Verification email requested" : loading ? "Requesting email…" : "Resend verification email"}
      </button>
      <p className="mt-5 text-center text-xs text-ink-faint"><Link href="/login" className="text-focus hover:underline">Return to sign in</Link></p>
    </AuthLayout>
  );
}

function AuthPageLoading() {
  return <div className="min-h-screen bg-ground" />;
}
