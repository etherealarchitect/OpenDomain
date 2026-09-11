import { create } from "zustand";
import { api } from "./api";

interface AuthState {
  token: string | null;
  user: { id: string; email: string; full_name: string; role: string } | null;
  loading: boolean;
  init: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
}

export const useAuth = create<AuthState>((set) => ({
  token: null,
  user: null,
  loading: true,

  init: async () => {
    const token = api.getToken();
    if (!token) {
      set({ loading: false });
      return;
    }
    try {
      const user = await api.get<AuthState["user"]>("/auth/me");
      set({ token, user, loading: false });
    } catch {
      api.clearToken();
      set({ token: null, user: null, loading: false });
    }
  },

  login: async (email, password) => {
    const res = await api.login(email, password);
    const user = await api.get<AuthState["user"]>("/auth/me");
    set({ token: res.access_token, user });
  },

  register: async (email, password, fullName) => {
    await api.register(email, password, fullName);
    const res = await api.login(email, password);
    const user = await api.get<AuthState["user"]>("/auth/me");
    set({ token: res.access_token, user });
  },

  logout: () => {
    api.clearToken();
    set({ token: null, user: null });
  },
}));
