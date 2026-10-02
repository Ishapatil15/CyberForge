import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { Loading } from "../components/ui/Feedback";

export function RequireAuth() {
  const { user, loading } = useAuth();
  if (loading) return <div className="p-8"><Loading /></div>;
  if (!user) return <Navigate to="/login" replace />;
  return <Outlet />;
}

export function GuestOnly() {
  const { user, loading } = useAuth();
  if (loading) return <div className="p-8"><Loading /></div>;
  if (user) return <Navigate to="/" replace />;
  return <Outlet />;
}
