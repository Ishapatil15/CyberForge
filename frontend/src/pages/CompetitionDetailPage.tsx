import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ApiError } from "../services/api";
import { Badge, difficultyTone } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { Alert, Loading } from "../components/ui/Feedback";
import {
  Swords,
  Clock,
  Users,
  Trophy,
  Flag,
  ShieldCheck,
  CheckCircle2,
  ArrowRight,
  AlertCircle,
  FileText,
} from "lucide-react";
import type { Competition } from "../types";

function useCountdown(endIso: string, serverNow: string) {
  const offset = useMemo(() => Date.now() - new Date(serverNow).getTime(), [serverNow]);
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, []);
  const remaining = new Date(endIso).getTime() - (now - offset);
  if (remaining <= 0) return "00:00:00";
  const s = Math.floor(remaining / 1000);
  const h = String(Math.floor(s / 3600)).padStart(2, "0");
  const m = String(Math.floor((s % 3600) / 60)).padStart(2, "0");
  const sec = String(s % 60).padStart(2, "0");
  return `${h}:${m}:${sec}`;
}

export default function CompetitionDetailPage() {
  const { id } = useParams();
  const [comp, setComp] = useState<Competition | null>(null);
  const [board, setBoard] = useState<Record<string, unknown>[]>([]);
  const [error, setError] = useState("");
  const [regLoading, setRegLoading] = useState(false);
  const countdown = useCountdown(
    comp?.end_at || new Date().toISOString(),
    comp?.server_now || new Date().toISOString()
  );

  async function load() {
    const data = await api.get<Competition>(`/api/competitions/${id}`);
    setComp(data);
    const lb = await api.get<{ items: Record<string, unknown>[] }>(`/api/competitions/${id}/leaderboard`);
    setBoard(lb.items);
  }

  useEffect(() => {
    void load();
  }, [id]);

  if (!comp) return <Loading />;

  const isActive = comp.status === "ACTIVE";

  return (
    <div className="mx-auto max-w-6xl space-y-6 pb-16">
      {/* Header row */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Swords className="h-5 w-5 text-forge-cyan" />
            <span className="font-mono text-xs uppercase tracking-wider text-forge-cyan">Wargame Arena</span>
          </div>
          <h1 className="mt-1 font-heading text-3xl font-bold text-forge-text">{comp.name}</h1>
          <p className="mt-1 text-sm text-forge-muted">{comp.description}</p>
        </div>

        <div className="flex items-center gap-2">
          <Badge tone={isActive ? "cyan" : "slate"}>{comp.status.replace("_", " ")}</Badge>
          <Badge tone="purple">{comp.mode} MODE</Badge>
          {comp.registered && (
            <Badge tone="emerald" className="gap-1">
              <CheckCircle2 className="h-3 w-3" /> REGISTERED
            </Badge>
          )}
        </div>
      </div>

      {error && <Alert>{error}</Alert>}

      {/* Statistics telemetry row */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <Card className="text-center py-4 border-forge-cyan/30 bg-forge-card shadow-cyan-sm">
          <p className="font-mono text-[11px] uppercase tracking-wider text-forge-muted flex items-center justify-center gap-1">
            <Clock className="h-3 w-3 text-forge-cyan" /> Time Remaining
          </p>
          <p className="mt-1 font-mono text-2xl font-bold text-forge-cyan">{countdown}</p>
        </Card>
        <Card className="text-center py-4">
          <p className="font-mono text-[11px] uppercase tracking-wider text-forge-muted flex items-center justify-center gap-1">
            <Users className="h-3 w-3 text-forge-purple" /> Contenders
          </p>
          <p className="mt-1 font-mono text-2xl font-bold text-forge-text">{comp.participant_count}</p>
        </Card>
        <Card className="text-center py-4">
          <p className="font-mono text-[11px] uppercase tracking-wider text-forge-muted flex items-center justify-center gap-1">
            <Flag className="h-3 w-3 text-forge-cyan" /> Challenges
          </p>
          <p className="mt-1 font-mono text-2xl font-bold text-forge-text">{comp.challenge_count}</p>
        </Card>
        <Card className="text-center py-4">
          <p className="font-mono text-[11px] uppercase tracking-wider text-forge-muted">Your Event Score</p>
          <p className="mt-1 font-mono text-2xl font-bold text-forge-cyan">
            {comp.my_score !== null && comp.my_score !== undefined ? `${comp.my_score} pts` : "—"}
          </p>
        </Card>
        <Card className="text-center py-4">
          <p className="font-mono text-[11px] uppercase tracking-wider text-forge-muted">Your Event Rank</p>
          <p className="mt-1 font-mono text-2xl font-bold text-forge-text">
            {comp.my_rank ? `#${comp.my_rank}` : "—"}
          </p>
        </Card>
      </div>

      {/* Registration callout if not registered */}
      {!comp.registered && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-xl border border-forge-cyan/30 bg-forge-cyan/10 p-5">
          <div className="space-y-1">
            <h3 className="font-heading font-semibold text-forge-text">Join this competition arena</h3>
            <p className="text-xs text-forge-muted">
              Registration is required to view live challenge clues and submit validated flags.
            </p>
          </div>
          <Button
            size="md"
            disabled={regLoading}
            onClick={async () => {
              setRegLoading(true);
              setError("");
              try {
                await api.post(`/api/competitions/${id}/register`);
                await load();
              } catch (err) {
                setError(err instanceof ApiError ? err.detail : "Registration failed");
              } finally {
                setRegLoading(false);
              }
            }}
          >
            {regLoading ? "Registering..." : "Register Now"}
          </Button>
        </div>
      )}

      {/* Rules of Engagement */}
      <Card className="space-y-3">
        <div className="flex items-center gap-2 border-b border-forge-border pb-2.5">
          <FileText className="h-4 w-4 text-forge-cyan" />
          <h2 className="font-heading font-semibold text-sm text-forge-text">Event Rules of Engagement</h2>
        </div>
        <pre className="whitespace-pre-wrap font-sans text-xs text-slate-300 leading-relaxed bg-transparent p-0 border-0">
          {comp.rules || "Standard competition ethics apply. No flag sharing. All attacks against platform infrastructure are strictly prohibited."}
        </pre>
        <p className="font-mono text-[10px] text-forge-subtle">
          * Countdown timer is synchronized with UTC server timestamps. Access windows are verified on backend.
        </p>
      </Card>

      {/* Challenges Section */}
      <Card className="space-y-4">
        <div className="flex items-center justify-between border-b border-forge-border pb-3">
          <h2 className="font-heading font-semibold text-base text-forge-text">Arena Challenges</h2>
          <span className="font-mono text-xs text-forge-muted">
            {comp.challenges?.length ?? 0} challenges available
          </span>
        </div>

        {comp.challenges && comp.challenges.length > 0 ? (
          <div className="grid gap-3 sm:grid-cols-2">
            {comp.challenges.map((c) => (
              <Link
                key={c.id}
                to={`/challenges/${c.id}?competition_id=${comp.id}`}
                className="flex items-center justify-between rounded-xl border border-forge-border bg-forge-bg/60 p-4 transition-all hover:border-forge-cyan/40 hover:bg-forge-surface group"
              >
                <div>
                  <h4 className="font-heading font-semibold text-sm text-forge-text group-hover:text-forge-cyan transition-colors">
                    {c.title}
                  </h4>
                  <p className="font-mono text-[11px] text-forge-muted mt-0.5">
                    {c.category.replace("_", " ")}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge tone={difficultyTone(c.difficulty)}>{c.difficulty}</Badge>
                  <span className="font-mono text-xs font-bold text-forge-cyan">{c.points}p</span>
                  {c.solved && (
                    <span title="Solved">
                      <CheckCircle2 className="h-4 w-4 text-forge-success" />
                    </span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <p className="text-xs font-mono text-forge-subtle py-4 text-center">
            {isActive
              ? "Register for this competition to access challenge objectives."
              : "Challenges will unlock automatically when the event start time is reached."}
          </p>
        )}
      </Card>

      {/* Live Event Leaderboard */}
      <Card className="overflow-x-auto p-0">
        <div className="p-5 border-b border-forge-border flex items-center justify-between">
          <h2 className="font-heading font-semibold text-base text-forge-text">Live Arena Leaderboard</h2>
          <span className="font-mono text-xs text-forge-cyan">SYNCED IN UTC</span>
        </div>
        <table className="w-full text-left text-sm">
          <thead className="bg-forge-surface/50 text-[11px] font-mono uppercase text-forge-muted border-b border-forge-border">
            <tr>
              <th className="px-5 py-3">Rank</th>
              <th>Contender / Squad</th>
              <th>Points</th>
              <th>Solves</th>
              <th>Last Solve Time</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-forge-border">
            {board.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-8 text-center text-xs font-mono text-forge-subtle">
                  No submissions recorded for this arena yet.
                </td>
              </tr>
            ) : (
              board.map((r) => (
                <tr key={String(r.rank)} className="hover:bg-white/[0.02]">
                  <td className="px-5 py-3.5 font-mono font-bold text-forge-cyan">#{String(r.rank)}</td>
                  <td className="font-medium text-forge-text">{String(r.username || r.team_name || "—")}</td>
                  <td className="font-mono font-bold text-forge-cyan">{String(r.points)}</td>
                  <td className="font-mono text-slate-300">{String(r.solves)}</td>
                  <td className="font-mono text-xs text-forge-muted">
                    {r.last_solve_at ? new Date(String(r.last_solve_at)).toLocaleString() : "—"}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
