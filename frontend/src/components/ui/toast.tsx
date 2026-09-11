"use client";

import { create } from "zustand";
import { useEffect } from "react";

interface Toast {
  id: string;
  message: string;
  type: "success" | "error" | "info";
}

interface ToastStore {
  toasts: Toast[];
  add: (message: string, type?: Toast["type"]) => void;
  remove: (id: string) => void;
}

export const useToastStore = create<ToastStore>((set) => ({
  toasts: [],
  add: (message, type = "info") => {
    const id = Math.random().toString(36).slice(2);
    set((s) => ({ toasts: [...s.toasts, { id, message, type }] }));
    setTimeout(() => {
      set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }));
    }, 4000);
  },
  remove: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}));

export function toast(message: string, type?: Toast["type"]) {
  useToastStore.getState().add(message, type);
}

export function Toaster() {
  const toasts = useToastStore((s) => s.toasts);
  const remove = useToastStore((s) => s.remove);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((t) => (
        <div
          key={t.id}
          role="alert"
          onClick={() => remove(t.id)}
          className={`cursor-pointer rounded-lg border px-4 py-3 text-sm shadow-lg transition-opacity ${
            t.type === "success"
              ? "border-live/30 bg-ground-raised text-live"
              : t.type === "error"
                ? "border-fault/30 bg-ground-raised text-fault"
                : "border-edge bg-ground-raised text-ink-dim"
          }`}
        >
          {t.message}
        </div>
      ))}
    </div>
  );
}
