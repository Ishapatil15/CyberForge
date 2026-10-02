import { useEffect, useState } from "react";
import { api } from "../../services/api";
import { Card } from "../../components/ui/Card";
import { Loading } from "../../components/ui/Feedback";

type Row = { id: number; actor: string | null; action: string; resource_type: string; resource_id: string | null; created_at: string };

export default function AdminActivity() {
  const [items, setItems] = useState<Row[] | null>(null);
  useEffect(() => {
    api.get<{ items: Row[] }>("/api/admin/activity").then((d) => setItems(d.items));
  }, []);
  if (!items) return <Loading />;
  return (
    <div className="space-y-2">
      {items.map((a) => (
        <Card key={a.id} className="flex justify-between text-sm">
          <span>{a.actor || "system"} · {a.action} · {a.resource_type} {a.resource_id}</span>
          <span className="text-slate-500">{new Date(a.created_at).toLocaleString()}</span>
        </Card>
      ))}
    </div>
  );
}
