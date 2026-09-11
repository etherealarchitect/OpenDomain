"use client";

import { Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AuthLayout } from "@/components/ui/auth-layout";
import { api } from "@/lib/api";

export default function VerifyEmailPage() {
  return <Suspense fallback={<AuthPageLoading />}><VerifyEmailContent /></Suspense>;
}

function VerifyEmailContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryToken = searchParams.get("token");
  const [token, setToken] = useState(queryToken);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!queryToken && window.location.hash.startsWith("#token=")) {
      setToken(decodeURIComponent(window.location.hash.slice("#token=".length)));
    }
  }, [queryToken]);

  useEffect(() => {
    if (!token) return;
    api.verifyEmail(token)
      .then((challenge) => router.replace(`/mfa/setup?challenge=${encodeURIComponent(challenge.challenge_id)}`))
      .catch((err) => setError(err instanceof Error ? err.message : "We could not verify this email link."));
  }, [router, token]);

  const pending = !token && !error;
  const description = error
    ? error
    : pending
      ? "Preparing your secure verification link."
      : "Please wait while we securely confirm your email address.";

  return (
    <AuthLayout eyebrow="Confirming email" title={error ? "Verification unavailable" : "Verifying your email"} description={description} footer={<Link href="/verify-email/pending" className="font-medium text-focus hover:underline">Request a new verification link</Link>}>
      {!error && <div className="mt-8 flex items-center gap-3 rounded-xl border border-edge bg-ground p-4 text-sm text-ink-dim"><span className="h-4 w-4 animate-spin rounded-full border-2 border-focus border-t-transparent" />{pending ? "Loading verification link…" : "Preparing your protected account…"}</div>}
    </AuthLayout>
  );
}

function AuthPageLoading() {
  return <div className="min-h-screen bg-ground" />;
}
