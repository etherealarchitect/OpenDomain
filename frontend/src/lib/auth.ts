import { create } from "zustand";
import { api, type AuthChallengeResponse, type UserResponse } from "./api";

interface AuthState {
  user: UserResponse | null;
  loading: boolean;
  init: () => Promise<void>;
  login: (email: string, password: string) => Promise<AuthChallengeResponse>;
  completeMfa: (challengeId: string, code: string) => Promise<{ user: UserResponse; backupCodes: string[] | null }>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => Promise<void>;
}

export const useAuth = create<AuthState>((set) => ({
  user: null,
  loading: true,

  init: async () => {
    try {
      const user = await api.getCurrentUser();
      set({ user, loading: false });
    } catch {
      set({ user: null, loading: false });
    }
  },

  login: (email, password) => api.login(email, password),

  completeMfa: async (challengeId, code) => {
    const result = await api.verifyMfa(challengeId, code);
    set({ user: result.user, loading: false });
    return { user: result.user, backupCodes: result.backup_codes };
  },

  register: async (email, password, fullName) => {
    await api.register(email, password, fullName);
  },

  logout: async () => {
    try {
      await api.logout();
    } finally {
      set({ user: null, loading: false });
    }
  },
}));
