import { useEffect, useState } from "react";
import { api } from "../../services/api";
import { Card } from "../../components/ui/Card";
import type { Team } from "../../types";
import { Loading } from "../../components/ui/Feedback";

export default function AdminTeams() {
  const [items, setItems] = useState<Team[] | null>(null);
  useEffect(() => {
    api.get<{ items: Team[] }>("/api/admin/teams").then((d) => setItems(d.items));
  }, []);
  if (!items) return <Loading />;
  return (
    <div className="space-y-3">
      {items.map((t) => (
        <Card key={t.id}>
          <p className="font-medium">{t.name}</p>
          <p className="text-sm text-slate-400">Captain {t.captain} · {t.members.map((m) => m.username).join(", ")}</p>
        </Card>
      ))}
    </div>
  );
}
