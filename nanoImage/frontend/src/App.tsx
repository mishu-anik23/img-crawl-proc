import { useEffect } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Workspace from "./pages/Workspace";
import { useAuthStore } from "./stores/authStore";

function AppRoutes() {
  const hydrate = useAuthStore((s) => s.hydrate);
  const user = useAuthStore((s) => s.user);

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/workspace" replace /> : <Login />} />
      <Route
        path="/register"
        element={user ? <Navigate to="/workspace" replace /> : <Register />}
      />
      <Route element={<ProtectedRoute />}>
        <Route path="/workspace" element={<Workspace />} />
      </Route>
      <Route path="*" element={<Navigate to={user ? "/workspace" : "/login"} replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}
