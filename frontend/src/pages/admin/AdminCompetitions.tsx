import { FormEvent, useEffect, useState } from "react";
import { api, ApiError } from "../../services/api";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Input, Label, Select, Textarea } from "../../components/ui/Field";
import { Alert, Loading } from "../../components/ui/Feedback";
import { Badge } from "../../components/ui/Badge";

type Comp = { id: number; name: string; status: string; start_at: string; end_at: string };

export default function AdminCompetitions() {
  const [items, setItems] = useState<Comp[] | null>(null);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    name: "Campus Invitational",
    slug: "campus-invitational",
    description: "Student practice cup",
    rules: "No attacking infrastructure. No flag sharing.",
    mode: "INDIVIDUAL",
    start_at: "",
    end_at: "",
    registration_start_at: "",
    registration_end_at: "",
  });

  async function load() {
    const d = await api.get<{ items: Comp[] }>("/api/admin/competitions");
    setItems(d.items);
  }
  useEffect(() => {
    const now = new Date();
    const iso = (d: Date) => new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
    setForm((f) => ({
      ...f,
      registration_start_at: iso(now),
      start_at: iso(new Date(now.getTime() + 3600000)),
      end_at: iso(new Date(now.getTime() + 8 * 3600000)),
      registration_end_at: iso(new Date(now.getTime() + 7 * 3600000)),
    }));
    void load();
  }, []);

  async function create(e: FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await api.post("/api/admin/competitions", {
        ...form,
        start_at: new Date(form.start_at).toISOString(),
        end_at: new Date(form.end_at).toISOString(),
        registration_start_at: new Date(form.registration_start_at).toISOString(),
        registration_end_at: new Date(form.registration_end_at).toISOString(),
        challenge_ids: [],
      });
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Create failed");
    }
  }

  if (!items) return <Loading />;
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div className="space-y-3">
        {items.map((c) => (
          <Card key={c.id} className="flex justify-between">
            <div>
              <p className="font-medium">{c.name}</p>
              <p className="text-xs text-slate-500">{new Date(c.start_at).toLocaleString()}</p>
            </div>
            <Badge tone="cyan">{c.status}</Badge>
          </Card>
        ))}
      </div>
      <Card>
        <h2 className="mb-3 font-medium">Create competition</h2>
        <form className="space-y-3" onSubmit={create}>
          {error && <Alert>{error}</Alert>}
          <div><Label>Name</Label><Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
          <div><Label>Slug</Label><Input value={form.slug} onChange={(e) => setForm({ ...form, slug: e.target.value })} /></div>
          <div><Label>Description</Label><Textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
          <div><Label>Rules</Label><Textarea value={form.rules} onChange={(e) => setForm({ ...form, rules: e.target.value })} /></div>
          <div>
            <Label>Mode</Label>
            <Select value={form.mode} onChange={(e) => setForm({ ...form, mode: e.target.value })}>
              <option>INDIVIDUAL</option>
              <option>TEAM</option>
            </Select>
          </div>
          <div><Label>Start</Label><Input type="datetime-local" value={form.start_at} onChange={(e) => setForm({ ...form, start_at: e.target.value })} /></div>
          <div><Label>End</Label><Input type="datetime-local" value={form.end_at} onChange={(e) => setForm({ ...form, end_at: e.target.value })} /></div>
          <div><Label>Registration start</Label><Input type="datetime-local" value={form.registration_start_at} onChange={(e) => setForm({ ...form, registration_start_at: e.target.value })} /></div>
          <div><Label>Registration end</Label><Input type="datetime-local" value={form.registration_end_at} onChange={(e) => setForm({ ...form, registration_end_at: e.target.value })} /></div>
          <Button>Create</Button>
        </form>
      </Card>
    </div>
  );
}
