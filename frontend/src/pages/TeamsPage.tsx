import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiError } from "../services/api";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { Input, Label, Textarea } from "../components/ui/Field";
import { Alert, EmptyState, Loading } from "../components/ui/Feedback";
import { useAuth } from "../hooks/useAuth";
import type { Team } from "../types";

export default function TeamsPage() {
  const { user, refresh } = useAuth();
  const [teams, setTeams] = useState<Team[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");
  const [profile, setProfile] = useState<{ team: { id: number; name: string } | null; invitations: { id: number; team_id: number; team_name: string }[] } | null>(null);

  async function load() {
    const [t, p] = await Promise.all([
      api.get<{ items: Team[] }>("/api/teams"),
      api.get<{ team: { id: number; name: string } | null; invitations: { id: number; team_id: number; team_name: string }[] }>("/api/users/me/profile"),
    ]);
    setTeams(t.items);
    setProfile(p);
  }

  useEffect(() => {
    void load();
  }, []);

  async function create(e: FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await api.post("/api/teams", { name, description });
      setName("");
      setDescription("");
      await load();
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Could not create team");
    }
  }

  if (!profile) return <Loading />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Teams</h1>
      {profile.invitations.length > 0 && (
        <Card>
          <h2 className="mb-3 font-medium">Invitations</h2>
          <ul className="space-y-2">
            {profile.invitations.map((i) => (
              <li key={i.id} className="flex items-center justify-between">
                <span>{i.team_name}</span>
                <div className="flex gap-2">
                  <Button onClick={async () => { await api.post(`/api/teams/invitations/${i.id}/accept`); await load(); }}>Accept</Button>
                  <Button variant="secondary" onClick={async () => { await api.post(`/api/teams/invitations/${i.id}/decline`); await load(); }}>Decline</Button>
                </div>
              </li>
            ))}
          </ul>
        </Card>
      )}
      {!profile.team && (
        <Card>
          <h2 className="mb-3 font-medium">Create a team</h2>
          <form className="space-y-3" onSubmit={create}>
            {error && <Alert>{error}</Alert>}
            <div>
              <Label>Team name</Label>
              <Input value={name} onChange={(e) => setName(e.target.value)} required />
            </div>
            <div>
              <Label>Description</Label>
              <Textarea value={description} onChange={(e) => setDescription(e.target.value)} />
            </div>
            <Button>Create team</Button>
          </form>
        </Card>
      )}
      {profile.team && (
        <p className="text-sm text-slate-400">
          You are on <Link className="text-cyan-300" to={`/teams/${profile.team.id}`}>{profile.team.name}</Link>
        </p>
      )}
      <div className="grid gap-4 md:grid-cols-2">
        {teams.length === 0 ? (
          <EmptyState title="No teams yet" body="Be the first captain on the platform." />
        ) : (
          teams.map((t) => (
            <Link key={t.id} to={`/teams/${t.id}`}>
              <Card>
                <h2 className="text-lg font-medium">{t.name}</h2>
                <p className="mt-1 text-sm text-slate-400">{t.description}</p>
                <p className="mt-3 font-mono text-cyan-300">{t.points} pts · {t.solves} solves {t.rank ? `· #${t.rank}` : ""}</p>
              </Card>
            </Link>
          ))
        )}
      </div>
      <p className="hidden">{user?.username}</p>
    </div>
  );
}
