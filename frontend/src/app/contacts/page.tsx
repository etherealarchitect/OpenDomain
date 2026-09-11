"use client";

import { useEffect, useState } from "react";
import { Shell } from "@/components/layout/shell";
import { api, type ContactResponse, type ContactCreate } from "@/lib/api";
import { toast } from "@/components/ui/toast";

const EMPTY_FORM: ContactCreate = {
  label: "",
  first_name: "",
  last_name: "",
  organization: "",
  email: "",
  phone: "",
  address_line1: "",
  address_line2: "",
  city: "",
  state_province: "",
  postal_code: "",
  country_code: "",
};

export default function ContactsPage() {
  const [contacts, setContacts] = useState<ContactResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<ContactCreate>({ ...EMPTY_FORM });
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState<string | null>(null);

  async function load() {
    try {
      const data = await api.listContacts();
      setContacts(data);
    } catch {
      toast("Failed to load contacts", "error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function openAdd() {
    setEditingId(null);
    setForm({ ...EMPTY_FORM });
    setShowForm(true);
  }

  function openEdit(c: ContactResponse) {
    setEditingId(c.id);
    setForm({
      label: c.label,
      first_name: c.first_name,
      last_name: c.last_name,
      organization: c.organization || "",
      email: c.email,
      phone: c.phone,
      address_line1: "",
      city: c.city,
      state_province: "",
      postal_code: "",
      country_code: c.country_code,
    });
    setShowForm(true);
  }

  function closeForm() {
    setShowForm(false);
    setEditingId(null);
    setForm({ ...EMPTY_FORM });
  }

  function setField(key: keyof ContactCreate, value: string) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);

    const payload: ContactCreate = {
      ...form,
      country_code: form.country_code.toUpperCase(),
    };

    try {
      if (editingId) {
        await api.updateContact(editingId, payload);
        toast("Contact updated", "success");
      } else {
        await api.createContact(payload);
        toast("Contact created", "success");
      }
      closeForm();
      await load();
    } catch (err) {
      toast(
        err instanceof Error ? err.message : "Failed to save contact",
        "error",
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: string) {
    setDeleting(id);
    try {
      await api.deleteContact(id);
      toast("Contact deleted", "success");
      setContacts((prev) => prev.filter((c) => c.id !== id));
    } catch (err) {
      toast(
        err instanceof Error ? err.message : "Failed to delete contact",
        "error",
      );
    } finally {
      setDeleting(null);
    }
  }

  return (
    <Shell>
      <div className="mx-auto max-w-4xl px-6 py-10">
        <div className="flex items-baseline justify-between">
          <h1 className="text-2xl font-semibold tracking-tight text-ink">
            Contacts
          </h1>
          {!showForm && (
            <button
              onClick={openAdd}
              className="rounded-md bg-focus px-3 py-1.5 text-sm font-medium text-ground transition-colors hover:bg-focus/90"
            >
              Add contact
            </button>
          )}
        </div>

        {showForm && (
          <form
            onSubmit={handleSave}
            className="mt-6 rounded-lg border border-edge bg-ground-raised p-5"
          >
            <h2 className="text-sm font-medium text-ink">
              {editingId ? "Edit contact" : "New contact"}
            </h2>

            <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Field
                label="Label"
                required
                value={form.label}
                onChange={(v) => setField("label", v)}
                placeholder="e.g. Personal, Business"
              />
              <div />
              <Field
                label="First name"
                required
                value={form.first_name}
                onChange={(v) => setField("first_name", v)}
              />
              <Field
                label="Last name"
                required
                value={form.last_name}
                onChange={(v) => setField("last_name", v)}
              />
              <Field
                label="Organization"
                value={form.organization || ""}
                onChange={(v) => setField("organization", v)}
              />
              <Field
                label="Email"
                required
                type="email"
                value={form.email}
                onChange={(v) => setField("email", v)}
              />
              <Field
                label="Phone"
                required
                value={form.phone}
                onChange={(v) => setField("phone", v)}
                placeholder="+1.5551234567"
              />
              <div />
              <Field
                label="Address"
                required
                value={form.address_line1}
                onChange={(v) => setField("address_line1", v)}
              />
              <Field
                label="Address line 2"
                value={form.address_line2 || ""}
                onChange={(v) => setField("address_line2", v)}
              />
              <Field
                label="City"
                required
                value={form.city}
                onChange={(v) => setField("city", v)}
              />
              <Field
                label="State / Province"
                value={form.state_province || ""}
                onChange={(v) => setField("state_province", v)}
              />
              <Field
                label="Postal code"
                required
                value={form.postal_code}
                onChange={(v) => setField("postal_code", v)}
              />
              <Field
                label="Country code"
                required
                value={form.country_code}
                onChange={(v) => setField("country_code", v)}
                placeholder="AU"
                maxLength={2}
              />
            </div>

            <div className="mt-5 flex gap-2">
              <button
                type="submit"
                disabled={saving}
                className="rounded-md bg-focus px-4 py-2 text-sm font-medium text-ground transition-colors hover:bg-focus/90 disabled:opacity-50"
              >
                {saving
                  ? "Saving..."
                  : editingId
                    ? "Update contact"
                    : "Create contact"}
              </button>
              <button
                type="button"
                onClick={closeForm}
                className="rounded-md border border-edge px-4 py-2 text-sm text-ink-dim transition-colors hover:bg-ground-overlay"
              >
                Cancel
              </button>
            </div>
          </form>
        )}

        {loading ? (
          <p className="mt-8 text-sm text-ink-faint">Loading contacts...</p>
        ) : contacts.length === 0 && !showForm ? (
          <div className="mt-8 rounded-lg border border-edge bg-ground-raised p-8 text-center">
            <p className="text-sm text-ink-dim">No contacts yet.</p>
            <p className="mt-1 text-xs text-ink-faint">
              You need at least one contact to register a domain.
            </p>
            <button
              onClick={openAdd}
              className="mt-4 rounded-md bg-focus px-4 py-2 text-sm font-medium text-ground transition-colors hover:bg-focus/90"
            >
              Add your first contact
            </button>
          </div>
        ) : (
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            {contacts.map((c) => (
              <div
                key={c.id}
                className="rounded-lg border border-edge bg-ground-raised p-4"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-ink">
                      {c.first_name} {c.last_name}
                    </p>
                    <p className="mt-0.5 text-xs text-ink-faint">{c.label}</p>
                  </div>
                  <div className="flex gap-1">
                    <button
                      onClick={() => openEdit(c)}
                      className="rounded px-2 py-1 text-xs text-ink-dim transition-colors hover:bg-ground-overlay hover:text-ink"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(c.id)}
                      disabled={deleting === c.id}
                      className="rounded px-2 py-1 text-xs text-fault/70 transition-colors hover:bg-fault/10 hover:text-fault disabled:opacity-50"
                    >
                      {deleting === c.id ? "..." : "Delete"}
                    </button>
                  </div>
                </div>
                <div className="mt-3 space-y-1 text-xs text-ink-dim">
                  <p>{c.email}</p>
                  <p>{c.phone}</p>
                  <p>
                    {c.city}, {c.country_code}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Shell>
  );
}

function Field({
  label,
  value,
  onChange,
  required,
  type = "text",
  placeholder,
  maxLength,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  required?: boolean;
  type?: string;
  placeholder?: string;
  maxLength?: number;
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
        maxLength={maxLength}
        className="rounded-md border border-edge bg-ground px-3 py-1.5 text-sm text-ink placeholder:text-ink-faint focus:border-focus focus:outline-none focus:ring-1 focus:ring-focus"
      />
    </label>
  );
}
