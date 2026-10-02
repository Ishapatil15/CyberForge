import { FormEvent, useEffect, useState } from "react";
import { api } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { Input, Label, Textarea } from "../components/ui/Field";
import { Loading } from "../components/ui/Feedback";

type Profile = {
  user: { username: string; email: string; avatar_url?: string | null; bio?: string | null; total_points: number };
  rank: number;
  solved: number;
  team: { name: string } | null;
  competitions: { id: number; name: string }[];
  recent_submissions: { id: number; challenge_title: string; is_correct: boolean; created_at: string }[];
};

export default function ProfilePage() {
  const { refresh } = useAuth();
  const [data, setData] = useState<Profile | null>(null);
  const [bio, setBio] = useState("");
  const [avatar, setAvatar] = useState("");

  useEffect(() => {
    api.get<Profile>("/api/users/me/profile").then((d) => {
      setData(d);
      setBio(d.user.bio || "");
      setAvatar(d.user.avatar_url || "");
    });
  }, []);

  async function save(e: FormEvent) {
    e.preventDefault();
    await api.patch("/api/auth/me", { bio, avatar_url: avatar || null });
    await refresh();
    const d = await api.get<Profile>("/api/users/me/profile");
    setData(d);
  }

  if (!data) return <Loading />;
  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <h1 className="text-2xl font-semibold">{data.user.username}</h1>
      <div className="grid gap-4 sm:grid-cols-3">
        <Card><p className="text-xs text-slate-500">Points</p><p className="mt-2 font-mono text-2xl text-cyan-300">{data.user.total_points}</p></Card>
        <Card><p className="text-xs text-slate-500">Rank</p><p className="mt-2 font-mono text-2xl">#{data.rank}</p></Card>
        <Card><p className="text-xs text-slate-500">Solved</p><p className="mt-2 font-mono text-2xl">{data.solved}</p></Card>
      </div>
      <Card>
        <p className="text-sm text-slate-400">Team: {data.team?.name || "None"}</p>
        <p className="mt-2 text-sm text-slate-400">
          Competitions: {data.competitions.length ? data.competitions.map((c) => c.name).join(", ") : "None yet"}
        </p>
      </Card>
      <Card>
        <form className="space-y-3" onSubmit={save}>
          <div>
            <Label>Avatar URL</Label>
            <Input value={avatar} onChange={(e) => setAvatar(e.target.value)} placeholder="https://…" />
          </div>
          <div>
            <Label>Bio</Label>
            <Textarea value={bio} onChange={(e) => setBio(e.target.value)} />
          </div>
          <Button>Save profile</Button>
        </form>
      </Card>
      <Card>
        <h2 className="mb-3 font-medium">Recent activity</h2>
        <ul className="space-y-2 text-sm">
          {data.recent_submissions.map((s) => (
            <li key={s.id} className="flex justify-between">
              <span>{s.challenge_title}</span>
              <span>{s.is_correct ? "Correct" : "Incorrect"}</span>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}
