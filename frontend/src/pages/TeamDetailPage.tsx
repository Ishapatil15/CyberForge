import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api, ApiError } from "../services/api";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { Input, Label } from "../components/ui/Field";
import { Alert, Loading } from "../components/ui/Feedback";
import { useAuth } from "../hooks/useAuth";
import type { Team } from "../types";

export default function TeamDetailPage() {
  const { id } = useParams();
  const { user, refresh } = useAuth();
  const navigate = useNavigate();
  const [team, setTeam] = useState<Team & { invitations?: { id: number; username: string }[] } | null>(null);
  const [username, setUsername] = useState("");
  const [error, setError] = useState("");

  async function load() {
    setTeam(await api.get(`/api/teams/${id}`));
  }

  useEffect(() => {
    void load();
  }, [id]);

  if (!team) return <Loading />;
  const isCaptain = user?.id === team.captain_id;
  const isMember = team.members.some((m) => m.id === user?.id);

  async function invite(e: FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await api.post(`/api/teams/${id}/invite`, { username });
      setUsername("");
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Invite failed");
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <h1 className="text-3xl font-semibold">{team.name}</h1>
      <Card>
        <p className="text-slate-300">{team.description}</p>
        <p className="mt-4 text-sm">Captain: {team.captain}</p>
        <p className="mt-2 font-mono text-cyan-300">
          Points: {team.points} · Solved: {team.solves} · Rank: {team.rank ? `#${team.rank}` : "—"}
        </p>
      </Card>
      <Card>
        <h2 className="mb-3 font-medium">Members</h2>
        <ul className="space-y-2">
          {team.members.map((m) => (
            <li key={m.id} className="flex items-center justify-between">
              <span>{m.username} · {m.points} pts</span>
              {isCaptain && m.id !== team.captain_id && (
                <Button variant="ghost" onClick={async () => { await api.post(`/api/teams/${id}/members/${m.id}/remove`); await load(); }}>
                  Remove
                </Button>
              )}
            </li>
          ))}
        </ul>
      </Card>
      {isCaptain && (
        <Card>
          <form className="space-y-3" onSubmit={invite}>
            {error && <Alert>{error}</Alert>}
            <Label>Invite username</Label>
            <Input value={username} onChange={(e) => setUsername(e.target.value)} />
            <Button>Send invite</Button>
          </form>
        </Card>
      )}
      {isMember && (
        <Button
          variant="secondary"
          onClick={async () => {
            await api.post(`/api/teams/${id}/leave`);
            await refresh();
            navigate("/teams");
          }}
        >
          Leave team
        </Button>
      )}
    </div>
  );
}
