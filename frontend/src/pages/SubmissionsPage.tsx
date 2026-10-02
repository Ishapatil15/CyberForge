import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import { Badge } from "../components/ui/Badge";
import { Card } from "../components/ui/Card";
import { EmptyState, Loading } from "../components/ui/Feedback";

type Row = {
  challenge_id: number;
  challenge: string;
  category: string;
  attempts: number;
  status: string;
  first_attempt: string;
  solved_at: string | null;
};

export default function SubmissionsPage() {
  const [items, setItems] = useState<Row[] | null>(null);
  useEffect(() => {
    api.get<{ items: Row[] }>("/api/users/me/submissions").then((d) => setItems(d.items));
  }, []);
  if (!items) return <Loading />;
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Submission history</h1>
      {items.length === 0 ? (
        <EmptyState title="No submissions yet" body="Your private attempt history will appear after you submit a flag." />
      ) : (
        <Card className="overflow-x-auto p-0">
          <table className="w-full text-left text-sm">
            <thead className="text-xs uppercase text-slate-500">
              <tr>
                <th className="px-5 py-3">Challenge</th>
                <th>Category</th>
                <th>Status</th>
                <th>Attempts</th>
                <th>First attempt</th>
                <th>Solved at</th>
              </tr>
            </thead>
            <tbody>
              {items.map((r) => (
                <tr key={r.challenge_id} className="border-t border-white/5">
                  <td className="px-5 py-3">
                    <Link className="text-cyan-300" to={`/challenges/${r.challenge_id}`}>{r.challenge}</Link>
                  </td>
                  <td>{r.category}</td>
                  <td><Badge tone={r.status === "Correct" ? "emerald" : "rose"}>{r.status}</Badge></td>
                  <td>{r.attempts}</td>
                  <td>{new Date(r.first_attempt).toLocaleString()}</td>
                  <td>{r.solved_at ? new Date(r.solved_at).toLocaleString() : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  );
}
