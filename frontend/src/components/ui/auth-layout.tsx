import Link from "next/link";
import type { ReactNode } from "react";

export function AuthLayout({
  eyebrow,
  title,
  description,
  children,
  footer,
}: {
  eyebrow: string;
  title: string;
  description: string;
  children: ReactNode;
  footer?: ReactNode;
}) {
  return (
    <main className="relative flex min-h-screen overflow-hidden bg-ground px-5 py-10 sm:items-center sm:justify-center sm:px-8">
      <div className="pointer-events-none absolute inset-0 opacity-40 [background-image:linear-gradient(var(--color-edge)_1px,transparent_1px),linear-gradient(90deg,var(--color-edge)_1px,transparent_1px)] [background-size:40px_40px] [mask-image:linear-gradient(to_bottom,black,transparent_70%)]" />
      <div className="relative z-10 w-full max-w-[440px]">
        <Link href="/" className="inline-flex items-center gap-2 font-mono text-sm font-medium tracking-tight text-ink transition-colors hover:text-focus">
          <span className="grid h-7 w-7 place-items-center rounded-md border border-focus/40 bg-focus/10 text-focus">&lt;.</span>
          opendomain
        </Link>
        <section className="mt-9 rounded-2xl border border-edge bg-ground-raised/95 p-6 shadow-2xl shadow-black/20 sm:p-8">
          <p className="font-mono text-[11px] font-medium uppercase tracking-[0.18em] text-focus">{eyebrow}</p>
          <h1 className="mt-3 text-2xl font-semibold tracking-tight text-ink sm:text-3xl">{title}</h1>
          <p className="mt-3 text-sm leading-6 text-ink-dim">{description}</p>
          {children}
        </section>
        {footer && <div className="mt-6 text-center text-xs leading-5 text-ink-faint">{footer}</div>}
      </div>
    </main>
  );
}

export function PasswordStrength({ password }: { password: string }) {
  const checks = [
    [password.length >= 12, "12+ characters"],
    [/[a-z]/.test(password), "Lowercase"],
    [/[A-Z]/.test(password), "Uppercase"],
    [/\d/.test(password), "Number"],
  ];
  const strength = checks.filter(([passed]) => passed).length;
  return (
    <div className="mt-2" aria-live="polite">
      <div className="flex gap-1" aria-label={`Password strength: ${strength} of 4`}>
        {checks.map(([passed], index) => <span key={index} className={`h-1 flex-1 rounded-full ${passed ? "bg-live" : "bg-edge"}`} />)}
      </div>
      <div className="mt-2 grid grid-cols-2 gap-x-2 gap-y-1 text-[11px] text-ink-faint">
        {checks.map(([passed, label]) => <span key={label as string} className={passed ? "text-live" : ""}>{passed ? "✓" : "○"} {label as string}</span>)}
      </div>
    </div>
  );
}
