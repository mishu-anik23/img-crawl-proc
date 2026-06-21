import { create } from "zustand";
import { fetchMe, login, register, type User } from "../services/api";

interface AuthState {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  hydrate: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  loading: false,
  error: null,

  login: async (email, password) => {
    set({ loading: true, error: null });
    try {
      const data = await login(email, password);
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      set({ user: data.user, loading: false });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Login failed";
      set({ error: message, loading: false });
      throw err;
    }
  },

  register: async (email, password, fullName) => {
    set({ loading: true, error: null });
    try {
      await register(email, password, fullName);
      set({ loading: false });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Registration failed";
      set({ error: message, loading: false });
      throw err;
    }
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    set({ user: null });
  },

  hydrate: async () => {
    const token = localStorage.getItem("access_token");
    if (!token) return;
    set({ loading: true });
    try {
      const user = await fetchMe();
      set({ user, loading: false });
    } catch {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      set({ user: null, loading: false });
    }
  },
}));
