import { useEffect, useState } from "react";
import { api } from "../../services/api";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Input, Select } from "../../components/ui/Field";
import { Loading } from "../../components/ui/Feedback";

type UserRow = { id: number; username: string; email: string; role: string; total_points: number; is_suspended: boolean };

export default function AdminUsers() {
  const [q, setQ] = useState("");
  const [items, setItems] = useState<UserRow[] | null>(null);
  async function load() {
    const d = await api.get<{ items: UserRow[] }>(`/api/admin/users?q=${encodeURIComponent(q)}`);
    setItems(d.items);
  }
  useEffect(() => {
    void load();
  }, [q]);
  if (!items) return <Loading />;
  return (
    <div className="space-y-3">
      <Input placeholder="Search users" value={q} onChange={(e) => setQ(e.target.value)} />
      {items.map((u) => (
        <Card key={u.id} className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="font-medium">{u.username}</p>
            <p className="text-sm text-slate-400">{u.email} · {u.total_points} pts</p>
          </div>
          <div className="flex gap-2">
            <Select
              value={u.role}
              onChange={async (e) => {
                await api.patch(`/api/admin/users/${u.id}/role`, { role: e.target.value });
                await load();
              }}
            >
              <option>USER</option>
              <option>CHALLENGE_AUTHOR</option>
              <option>ADMIN</option>
            </Select>
            <Button
              variant={u.is_suspended ? "secondary" : "danger"}
              onClick={async () => {
                await api.patch(`/api/admin/users/${u.id}/suspend`, { is_suspended: !u.is_suspended });
                await load();
              }}
            >
              {u.is_suspended ? "Unsuspend" : "Suspend"}
            </Button>
          </div>
        </Card>
      ))}
    </div>
  );
}
