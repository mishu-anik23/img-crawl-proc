import { useEffect, useState } from "react";
import { useAuthStore } from "../stores/authStore";
import { checkHealth } from "../services/api";

export default function Workspace() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const [health, setHealth] = useState<string>("checking...");

  useEffect(() => {
    checkHealth()
      .then((data) => setHealth(`${data.service}: ${data.status}`))
      .catch(() => setHealth("offline"));
  }, []);

  return (
    <div className="flex min-h-screen flex-col bg-[#f8f9fa]">
      <header className="flex items-center justify-between border-b border-gray-200 bg-white px-6 py-4">
        <div className="flex items-center gap-3">
          <span className="text-xl font-bold text-[#6c63ff]">nanoImage</span>
          <span className="rounded-full bg-[#00d4ff]/10 px-3 py-0.5 text-xs font-medium text-[#00d4ff]">
            Phase 1
          </span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">{user?.email}</span>
          <button
            onClick={logout}
            className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm hover:bg-gray-50"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="flex flex-1 gap-4 p-4">
        <aside className="w-64 shrink-0 rounded-xl bg-white p-4 shadow-sm">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-400">
            Upload
          </h2>
          <div className="rounded-lg border-2 border-dashed border-gray-200 p-6 text-center text-sm text-gray-400">
            Drop images here
            <br />
            <span className="text-xs">(Phase 2)</span>
          </div>
        </aside>

        <section className="flex flex-1 flex-col gap-4">
          <div className="rounded-xl bg-white p-6 shadow-sm">
            <h2 className="mb-2 text-lg font-semibold">Prompt workspace</h2>
            <textarea
              placeholder="Describe the image you want to create..."
              rows={4}
              disabled
              className="w-full resize-none rounded-lg border border-gray-200 bg-gray-50 p-3 text-sm text-gray-400"
            />
            <p className="mt-2 text-xs text-gray-400">Gemini enhancement — Phase 3</p>
          </div>

          <div className="flex-1 rounded-xl bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold">Gallery</h2>
            <div className="grid grid-cols-4 gap-3">
              {[1, 2, 3, 4].map((n) => (
                <div
                  key={n}
                  className="aspect-square rounded-lg bg-gray-100 flex items-center justify-center text-xs text-gray-400"
                >
                  Placeholder
                </div>
              ))}
            </div>
          </div>
        </section>

        <aside className="w-80 shrink-0 rounded-xl bg-white p-4 shadow-sm">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-400">
            Settings
          </h2>
          <div className="space-y-3 text-sm text-gray-500">
            <p>Business model — Phase 5</p>
            <p>Niche — Phase 5</p>
            <p>Design type — Phase 5</p>
            <p>Style — Phase 5</p>
          </div>
          <div className="mt-6 rounded-lg bg-gray-50 p-3 text-xs text-gray-500">
            API: {health}
          </div>
        </aside>
      </main>
    </div>
  );
}
