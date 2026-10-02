import { NavLink, Outlet, Navigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

export default function AdminLayout() {
  const { user } = useAuth();
  if (user?.role !== "ADMIN" && user?.role !== "CHALLENGE_AUTHOR") {
    return <Navigate to="/" replace />;
  }
  const admin = user.role === "ADMIN";
  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-semibold">Administration</h1>
      <div className="flex flex-wrap gap-2">
        {admin && <Tab to="/admin">Dashboard</Tab>}
        <Tab to="/admin/challenges">Challenges</Tab>
        {admin && <Tab to="/admin/labs">Web Labs</Tab>}
        {admin && <Tab to="/admin/users">Users</Tab>}
        {admin && <Tab to="/admin/teams">Teams</Tab>}
        {admin && <Tab to="/admin/competitions">Competitions</Tab>}
        {admin && <Tab to="/admin/submissions">Submissions</Tab>}
        {admin && <Tab to="/admin/activity">Activity</Tab>}
      </div>
      <Outlet />
    </div>
  );
}

function Tab({ to, children }: { to: string; children: string }) {
  return (
    <NavLink
      to={to}
      end
      className={({ isActive }) =>
        `rounded-lg border px-3.5 py-1.5 text-xs font-semibold transition-all ${
          isActive
            ? "border-forge-cyan bg-forge-cyan/15 text-forge-cyan shadow-cyan-sm"
            : "border-forge-border bg-forge-card text-slate-400 hover:border-slate-600 hover:text-slate-200"
        }`
      }
    >
      {children}
    </NavLink>
  );
}
