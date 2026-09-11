"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { AuthLayout } from "@/components/ui/auth-layout";

export default function RecoveryCodesPage() {
  const router = useRouter();
  const [codes, setCodes] = useState<string[]>([]);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const stored = sessionStorage.getItem("opendomain-recovery-codes");
    if (stored) {
      try { setCodes(JSON.parse(stored)); } catch { router.replace("/dashboard"); }
    } else {
      router.replace("/dashboard");
    }
  }, [router]);

  function download() {
    const blob = new Blob([`OpenDomain recovery codes\nGenerated: ${new Date().toISOString()}\n\n${codes.join("\n")}\n`], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "opendomain-recovery-codes.txt";
    link.click();
    URL.revokeObjectURL(url);
    setSaved(true);
  }

  function continueToDashboard() {
    sessionStorage.removeItem("opendomain-recovery-codes");
    router.replace("/dashboard");
  }

  return <AuthLayout eyebrow="Keep these safe" title="Save your recovery codes" description="Use a recovery code if you lose access to your authenticator app. Each code works once, and these codes will not be shown again.">
    <div className="mt-7 rounded-xl border border-caution/30 bg-caution/10 px-4 py-3 text-sm leading-6 text-ink-dim">Store these in a password manager or another secure offline location. Do not save them in a shared document.</div>
    <div className="mt-5 grid grid-cols-2 gap-2 rounded-xl border border-edge bg-ground p-4 font-mono text-sm text-ink">
      {codes.map((code) => <span key={code} className="rounded bg-ground-raised px-2 py-1.5">{code}</span>)}
    </div>
    <button onClick={download} disabled={!codes.length} className="mt-5 w-full rounded-lg border border-edge px-4 py-3 text-sm font-medium text-ink transition hover:border-focus hover:text-focus disabled:opacity-50">Download recovery codes</button>
    <label className="mt-4 flex cursor-pointer items-start gap-2 text-xs leading-5 text-ink-dim"><input type="checkbox" checked={saved} onChange={(event) => setSaved(event.target.checked)} className="mt-1 accent-focus" />I have securely saved these recovery codes.</label>
    <button onClick={continueToDashboard} disabled={!saved} className="mt-5 w-full rounded-lg bg-focus px-4 py-3 text-sm font-semibold text-ground transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60">Continue to dashboard</button>
  </AuthLayout>;
}
