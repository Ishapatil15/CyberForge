import { useEffect, useState } from "react";
import { api } from "../../services/api";
import { Card } from "../../components/ui/Card";
import { useAuth } from "../../hooks/useAuth";
import { Navigate } from "react-router-dom";
import { Loading } from "../../components/ui/Feedback";

type Stats = {
  total_users: number;
  active_users: number;
  total_challenges: number;
  total_competitions: number;
  total_submissions: number;
  active_competitions: number;
};

export default function AdminHome() {
  const { user } = useAuth();
  const [stats, setStats] = useState<Stats | null>(null);
  useEffect(() => {
    if (user?.role === "ADMIN") {
      api.get<Stats>("/api/admin/dashboard").then(setStats);
    }
  }, [user]);
  if (user?.role !== "ADMIN") return <Navigate to="/admin/challenges" replace />;
  if (!stats) return <Loading />;
  const cells: [string, number][] = [
    ["Total users", stats.total_users],
    ["Active users", stats.active_users],
    ["Challenges", stats.total_challenges],
    ["Competitions", stats.total_competitions],
    ["Submissions", stats.total_submissions],
    ["Active competitions", stats.active_competitions],
  ];
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {cells.map(([k, v]) => (
        <Card key={k}>
          <p className="text-xs uppercase text-slate-500">{k}</p>
          <p className="mt-2 font-mono text-3xl text-cyan-300">{v}</p>
        </Card>
      ))}
    </div>
  );
}
