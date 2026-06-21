import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

export const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_BASE}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          });
          localStorage.setItem("access_token", data.access_token);
          original.headers.Authorization = `Bearer ${data.access_token}`;
          return api(original);
        } catch {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
        }
      }
    }
    return Promise.reject(error);
  },
);

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>("/api/v1/auth/login", { email, password });
  return data;
}

export async function register(
  email: string,
  password: string,
  fullName?: string,
): Promise<User> {
  const { data } = await api.post<User>("/api/v1/auth/register", {
    email,
    password,
    full_name: fullName,
  });
  return data;
}

export async function fetchMe(): Promise<User> {
  const { data } = await api.get<User>("/api/v1/auth/me");
  return data;
}

export async function checkHealth(): Promise<{ status: string; service: string }> {
  const { data } = await api.get("/health");
  return data;
}
