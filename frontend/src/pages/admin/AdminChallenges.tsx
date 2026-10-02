import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../services/api";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { EmptyState, Loading } from "../../components/ui/Feedback";
import type { Challenge } from "../../types";

export default function AdminChallenges() {
  const [items, setItems] = useState<Challenge[] | null>(null);
  async function load() {
    const d = await api.get<{ items: Challenge[] }>("/api/admin/challenges");
    setItems(d.items);
  }
  useEffect(() => {
    void load();
  }, []);
  if (!items) return <Loading />;
  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Link to="/admin/challenges/new"><Button>New challenge</Button></Link>
      </div>
      {items.length === 0 ? (
        <EmptyState title="No challenges" body="Create one with the editor." />
      ) : (
        items.map((c) => (
          <Card key={c.id} className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="font-medium">{c.title}</p>
              <p className="text-sm text-slate-400">{c.category} · {c.points} pts</p>
            </div>
            <div className="flex items-center gap-2">
              <Badge tone={c.is_published ? "emerald" : "amber"}>{c.is_published ? "Published" : "Draft"}</Badge>
              <Link to={`/admin/challenges/${c.id}`}><Button variant="secondary">Edit</Button></Link>
              <Button
                variant="danger"
                onClick={async () => {
                  await api.delete(`/api/admin/challenges/${c.id}`);
                  await load();
                }}
              >
                Archive
              </Button>
            </div>
          </Card>
        ))
      )}
    </div>
  );
}
