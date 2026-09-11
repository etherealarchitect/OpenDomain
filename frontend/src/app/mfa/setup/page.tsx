"use client";

import { Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AuthLayout } from "@/components/ui/auth-layout";
import { api, type MfaEnrollmentResponse } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function MfaSetupPage() {
  return <Suspense fallback={<AuthPageLoading />}><MfaSetupContent /></Suspense>;
}

function MfaSetupContent() {
  const router = useRouter();
  const challenge = useSearchParams().get("challenge");
  const { completeMfa } = useAuth();
  const [setup, setSetup] = useState<MfaEnrollmentResponse | null>(null);
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!challenge) {
      setError("Your authenticator setup session is missing or expired.");
      return;
    }
    api.startMfaEnrollment(challenge).then(setSetup).catch((err) => setError(err instanceof Error ? err.message : "We could not start authenticator setup."));
  }, [challenge]);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!challenge) return;
    setError("");
    setLoading(true);
    try {
      const result = await completeMfa(challenge, code);
      if (result.backupCodes) {
        sessionStorage.setItem("opendomain-recovery-codes", JSON.stringify(result.backupCodes));
        router.push("/recovery-codes");
      } else {
        router.push("/dashboard");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "That code could not be verified.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout eyebrow="Required protection" title="Set up your authenticator" description="Open your authenticator app, add this account, then enter the six-digit code it gives you." footer={<Link href="/login" className="font-medium text-focus hover:underline">Return to sign in</Link>}>
      {error ? <div role="alert" className="mt-7 rounded-lg border border-fault/30 bg-fault/10 px-3 py-2.5 text-sm text-fault">{error}</div> : !setup ? <div className="mt-8 flex items-center gap-3 rounded-xl border border-edge bg-ground p-4 text-sm text-ink-dim"><span className="h-4 w-4 animate-spin rounded-full border-2 border-focus border-t-transparent" />Generating your secure setup…</div> : <>
        <div className="mt-7 grid gap-5 sm:grid-cols-[150px_1fr] sm:items-center">
          <div className="grid aspect-square place-items-center rounded-xl bg-white p-2"><img src={setup.qr_data_uri} alt="QR code for OpenDomain authenticator setup" className="h-full w-full" /></div>
          <div>
            <p className="font-mono text-xs text-live">01 / SCAN QR CODE</p>
            <p className="mt-2 text-sm leading-6 text-ink-dim">Can’t scan it? Add an account manually with this setup key:</p>
            <code className="mt-3 block break-all rounded-lg border border-edge bg-ground px-3 py-2 text-xs text-ink">{setup.secret}</code>
          </div>
        </div>
        <form onSubmit={submit} className="mt-6">
          <label className="block"><span className="text-xs font-medium text-ink-dim">Six-digit code</span><input autoComplete="one-time-code" inputMode="numeric" pattern="[0-9]{6}" maxLength={6} value={code} onChange={(event) => setCode(event.target.value.replace(/\D/g, ""))} required placeholder="000000" className="mt-1.5 w-full rounded-lg border border-edge bg-ground px-3 py-3 font-mono text-lg tracking-[0.35em] text-ink outline-none transition focus:border-focus focus:ring-2 focus:ring-focus/20" /></label>
          <button disabled={loading || code.length !== 6} type="submit" className="mt-4 w-full rounded-lg bg-focus px-4 py-3 text-sm font-semibold text-ground transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60">{loading ? "Confirming authenticator…" : "Secure my account"}</button>
        </form>
      </>}
    </AuthLayout>
  );
}

function AuthPageLoading() {
  return <div className="min-h-screen bg-ground" />;
}
