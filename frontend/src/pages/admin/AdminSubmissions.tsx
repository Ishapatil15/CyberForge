import { useEffect, useState } from "react";
import { api } from "../../services/api";
import { Badge } from "../../components/ui/Badge";
import { Card } from "../../components/ui/Card";
import { Loading } from "../../components/ui/Feedback";

type Row = { id: number; username: string; challenge: string; competition: string | null; is_correct: boolean; created_at: string };

export default function AdminSubmissions() {
  const [items, setItems] = useState<Row[] | null>(null);
  useEffect(() => {
    api.get<{ items: Row[] }>("/api/admin/submissions").then((d) => setItems(d.items));
  }, []);
  if (!items) return <Loading />;
  return (
    <Card className="overflow-x-auto p-0">
      <table className="w-full text-left text-sm">
        <thead className="text-xs uppercase text-slate-500">
          <tr>
            <th className="px-5 py-3">User</th>
            <th>Challenge</th>
            <th>Competition</th>
            <th>Result</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          {items.map((r) => (
            <tr key={r.id} className="border-t border-white/5">
              <td className="px-5 py-3">{r.username}</td>
              <td>{r.challenge}</td>
              <td>{r.competition || "—"}</td>
              <td><Badge tone={r.is_correct ? "emerald" : "rose"}>{r.is_correct ? "Correct" : "Incorrect"}</Badge></td>
              <td>{new Date(r.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}
