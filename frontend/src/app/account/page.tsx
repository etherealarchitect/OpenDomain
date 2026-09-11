"use client";

import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/shell";
import { api, type UserResponse } from "@/lib/api";
import { toast } from "@/components/ui/toast";

export default function AccountPage() {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const [fullName, setFullName] = useState("");
  const [company, setCompany] = useState("");
  const [phone, setPhone] = useState("");
  const [savingProfile, setSavingProfile] = useState(false);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [savingPassword, setSavingPassword] = useState(false);

  useEffect(() => {
    api
      .getMe()
      .then((u) => {
        setUser(u);
        setFullName(u.full_name || "");
        setCompany(u.company || "");
        setPhone(u.phone || "");
      })
      .catch(() => toast("Failed to load account", "error"))
      .finally(() => setLoading(false));
  }, []);

  async function saveProfile(e: React.FormEvent) {
    e.preventDefault();
    setSavingProfile(true);
    try {
      const updated = await api.updateMe({
        full_name: fullName,
        company: company || undefined,
        phone: phone || undefined,
      });
      setUser(updated);
      toast("Profile updated", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to save", "error");
    } finally {
      setSavingProfile(false);
    }
  }

  async function changePassword(e: React.FormEvent) {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      toast("Passwords do not match", "error");
      return;
    }
    if (newPassword.length < 8) {
      toast("Password must be at least 8 characters", "error");
      return;
    }
    setSavingPassword(true);
    try {
      await api.changePassword(currentPassword, newPassword);
      toast("Password changed", "success");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to change password", "error");
    } finally {
      setSavingPassword(false);
    }
  }

  return (
    <Shell>
      <div className="mx-auto max-w-2xl px-6 py-10">
        <h1 className="text-2xl font-semibold tracking-tight text-ink">Account</h1>

        {loading ? (
          <p className="mt-8 text-sm text-ink-faint">Loading...</p>
        ) : (
          <>
            {user && (
              <div className="mt-6 rounded-lg border border-edge bg-ground-raised p-4">
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-xs text-ink-faint">Email</p>
                    <p className="mt-0.5 font-mono text-ink">{user.email}</p>
                  </div>
                  <div>
                    <p className="text-xs text-ink-faint">Role</p>
                    <p className="mt-0.5 text-ink capitalize">{user.role}</p>
                  </div>
                  <div>
                    <p className="text-xs text-ink-faint">Member since</p>
                    <p className="mt-0.5 text-ink">
                      {new Date(user.created_at).toLocaleDateString("en-AU", {
                        year: "numeric",
                        month: "short",
                        day: "numeric",
                      })}
                    </p>
                  </div>
                </div>
              </div>
            )}

            <form onSubmit={saveProfile} className="mt-8">
              <h2 className="text-sm font-medium text-ink">Profile</h2>
              <div className="mt-4 grid gap-4">
                <InputField label="Full name" value={fullName} onChange={setFullName} required />
                <InputField label="Company" value={company} onChange={setCompany} />
                <InputField label="Phone" value={phone} onChange={setPhone} placeholder="+61..." />
              </div>
              <button
                type="submit"
                disabled={savingProfile}
                className="mt-4 rounded-md bg-focus px-4 py-2 text-sm font-medium text-ground transition-colors hover:bg-focus/90 disabled:opacity-50"
              >
                {savingProfile ? "Saving..." : "Save profile"}
              </button>
            </form>

            <form onSubmit={changePassword} className="mt-10 border-t border-edge pt-8">
              <h2 className="text-sm font-medium text-ink">Change password</h2>
              <div className="mt-4 grid gap-4">
                <InputField
                  label="Current password"
                  value={currentPassword}
                  onChange={setCurrentPassword}
                  type="password"
                  required
                />
                <InputField
                  label="New password"
                  value={newPassword}
                  onChange={setNewPassword}
                  type="password"
                  required
                />
                <InputField
                  label="Confirm new password"
                  value={confirmPassword}
                  onChange={setConfirmPassword}
                  type="password"
                  required
                />
              </div>
              <button
                type="submit"
                disabled={savingPassword}
                className="mt-4 rounded-md bg-focus px-4 py-2 text-sm font-medium text-ground transition-colors hover:bg-focus/90 disabled:opacity-50"
              >
                {savingPassword ? "Changing..." : "Change password"}
              </button>
            </form>
          </>
        )}
      </div>
    </Shell>
  );
}

function InputField({
  label,
  value,
  onChange,
  type = "text",
  required,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  required?: boolean;
  placeholder?: string;
}) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-xs text-ink-dim">
        {label}
        {required && <span className="text-fault/60"> *</span>}
      </span>
      <input
        type={type}
        required={required}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="rounded-md border border-edge bg-ground px-3 py-1.5 text-sm text-ink placeholder:text-ink-faint focus:border-focus focus:outline-none focus:ring-1 focus:ring-focus"
      />
    </label>
  );
}
