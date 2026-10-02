import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import { Card } from "../components/ui/Card";
import { Badge, difficultyTone } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { EmptyState, Loading } from "../components/ui/Feedback";
import {
  LayoutDashboard,
  Trophy,
  Flame,
  Award,
  Swords,
  Users,
  Target,
  ArrowRight,
  CheckCircle2,
  Clock,
} from "lucide-react";
import type { Challenge, Competition } from "../types";

type DashboardData = {
  rank: number;
  solved: number;
  attempted: number;
  team: { id: number; name: string } | null;
  progress_by_category: { category: string; solved: number }[];
  recent_submissions: { id: number; challenge_title: string; is_correct: boolean; created_at: string }[];
  active_competitions: Competition[];
  recent_challenges: Challenge[];
  recommended_challenges: Challenge[];
};

function calculateLevel(points: number) {
  if (points >= 2000) return { level: 5, title: "Master Operative", next: "MAX LEVEL", progress: 100 };
  if (points >= 1000) return { level: 4, title: "Cyber Elite", next: "2000 PTS", progress: Math.min(100, Math.round(((points - 1000) / 1000) * 100)) };
  if (points >= 500) return { level: 3, title: "Senior Analyst", next: "1000 PTS", progress: Math.min(100, Math.round(((points - 500) / 500) * 100)) };
  if (points >= 200) return { level: 2, title: "Security Specialist", next: "500 PTS", progress: Math.min(100, Math.round(((points - 200) / 300) * 100)) };
  return { level: 1, title: "Cadet Operative", next: "200 PTS", progress: Math.min(100, Math.round((points / 200) * 100)) };
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get<DashboardData>("/api/users/me/dashboard")
      .then(setData)
      .catch(() => setError("Failed to initialize telemetry dashboard"));
  }, []);

  if (!data && !error) return <Loading />;

  const points = user?.total_points ?? 0;
  const levelInfo = calculateLevel(points);
  // Estimate streak based on solves/submissions
  const streak = data?.solved ? Math.max(1, Math.min(data.solved, 7)) : 0;

  return (
    <div className="mx-auto max-w-7xl space-y-6 pb-16">
      {/* Top Welcome Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <LayoutDashboard className="h-5 w-5 text-forge-cyan" />
            <span className="font-mono text-xs uppercase tracking-wider text-forge-cyan">Command Center</span>
          </div>
          <h1 className="mt-1 font-heading text-3xl font-bold text-forge-text">
            Welcome back, {user?.username}
          </h1>
          <p className="mt-1 text-sm text-forge-muted">
            Live telemetry, active arena standing, and domain competency progression.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link to="/challenges">
            <Button size="sm">Explore Challenges</Button>
          </Link>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {/* User Level */}
        <Card className="flex flex-col justify-between py-4">
          <div>
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs text-forge-muted uppercase">Rank Tier</span>
              <Award className="h-4 w-4 text-forge-purple" />
            </div>
            <p className="mt-2 font-heading text-xl font-bold text-forge-text">Lvl {levelInfo.level}</p>
            <p className="text-xs text-forge-cyan font-mono">{levelInfo.title}</p>
          </div>
          <div className="mt-3">
            <div className="h-1.5 w-full rounded-full bg-forge-bg overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-forge-purple to-forge-cyan rounded-full transition-all duration-500"
                style={{ width: `${levelInfo.progress}%` }}
              />
            </div>
            <span className="mt-1 block text-[10px] font-mono text-forge-subtle text-right">
              Target: {levelInfo.next}
            </span>
          </div>
        </Card>

        {/* Total Points */}
        <Card className="py-4">
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs text-forge-muted uppercase">Total Points</span>
            <Trophy className="h-4 w-4 text-forge-cyan" />
          </div>
          <p className="mt-2 font-mono text-3xl font-bold text-forge-cyan">{points}</p>
          <span className="mt-1 block text-[11px] font-mono text-forge-muted">Verified Solves</span>
        </Card>

        {/* Global Rank */}
        <Card className="py-4">
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs text-forge-muted uppercase">Global Standing</span>
            <span className="font-mono text-[10px] text-forge-cyan">WORLD</span>
          </div>
          <p className="mt-2 font-mono text-3xl font-bold text-forge-text">
            {data?.rank ? `#${data.rank}` : "—"}
          </p>
          <span className="mt-1 block text-[11px] font-mono text-forge-muted">Deterministic tie-break</span>
        </Card>

        {/* Challenges Solved */}
        <Card className="py-4">
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs text-forge-muted uppercase">Solved / Attempts</span>
            <Target className="h-4 w-4 text-forge-success" />
          </div>
          <p className="mt-2 font-mono text-3xl font-bold text-forge-success">
            {data?.solved ?? 0}{" "}
            <span className="text-sm font-normal text-forge-muted">/ {data?.attempted ?? 0}</span>
          </p>
          <span className="mt-1 block text-[11px] font-mono text-forge-muted">
            {data?.attempted ? `${Math.round(((data?.solved ?? 0) / data.attempted) * 100)}% accuracy` : "Ready to submit"}
          </span>
        </Card>

        {/* Current Streak */}
        <Card className="py-4">
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs text-forge-muted uppercase">Current Streak</span>
            <Flame className="h-4 w-4 text-forge-warning" />
          </div>
          <p className="mt-2 font-mono text-3xl font-bold text-forge-warning">
            {streak} <span className="text-sm font-normal text-forge-muted">days</span>
          </p>
          <span className="mt-1 block text-[11px] font-mono text-forge-muted">
            {streak > 0 ? "Daily solve active" : "Start your streak today"}
          </span>
        </Card>
      </div>

      {/* Middle Row: Active Competitions & Squad */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Active Competitions */}
        <Card className="space-y-3">
          <div className="flex items-center justify-between border-b border-forge-border pb-3">
            <div className="flex items-center gap-2">
              <Swords className="h-4 w-4 text-forge-cyan" />
              <h2 className="font-heading font-semibold text-base text-forge-text">Active Competitions</h2>
            </div>
            <Link to="/competitions" className="text-xs font-mono text-forge-cyan hover:underline">
              View All Arenas →
            </Link>
          </div>

          {data?.active_competitions && data.active_competitions.length > 0 ? (
            <div className="space-y-2.5">
              {data.active_competitions.map((c) => (
                <Link
                  key={c.id}
                  to={`/competitions/${c.id}`}
                  className="flex items-center justify-between rounded-lg border border-forge-border bg-forge-bg/60 p-3 transition hover:border-forge-cyan/40 hover:bg-forge-surface"
                >
                  <div>
                    <p className="font-medium text-sm text-forge-text">{c.name}</p>
                    <p className="font-mono text-[11px] text-forge-muted">{c.challenge_count} challenges • {c.participant_count} contenders</p>
                  </div>
                  <Badge tone="cyan">{c.status.replace("_", " ")}</Badge>
                </Link>
              ))}
            </div>
          ) : (
            <EmptyState
              title="No Live Competitions"
              body="No scheduled tournaments currently running. Practice standalone challenges or check back soon."
            />
          )}
        </Card>

        {/* Squad / Team Information */}
        <Card className="space-y-3">
          <div className="flex items-center justify-between border-b border-forge-border pb-3">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-forge-purple" />
              <h2 className="font-heading font-semibold text-base text-forge-text">Team Affiliation</h2>
            </div>
            <Link to="/teams" className="text-xs font-mono text-forge-cyan hover:underline">
              Manage Squads →
            </Link>
          </div>

          {data?.team ? (
            <div className="rounded-xl border border-forge-border bg-forge-bg/60 p-5 space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <span className="font-mono text-[10px] text-forge-muted uppercase">ASSIGNED SQUAD</span>
                  <h3 className="font-heading text-xl font-bold text-forge-text">{data.team.name}</h3>
                </div>
                <Link to={`/teams/${data.team.id}`}>
                  <Button variant="secondary" size="sm">
                    Team HQ
                  </Button>
                </Link>
              </div>
              <p className="text-xs text-forge-muted">
                Compete jointly in Team Mode competitions. Your solve points contribute to team aggregated leaderboard ranking.
              </p>
            </div>
          ) : (
            <EmptyState
              title="No Team Affiliation"
              body="Form a squad with university peers or accept pending invitations to compete in Team events."
              action={
                <Link to="/teams">
                  <Button variant="secondary" size="sm">
                    Create or Join Squad
                  </Button>
                </Link>
              }
            />
          )}
        </Card>
      </div>

      {/* Progress by Category & Recent Submissions */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Progress by Category Bars */}
        <Card className="space-y-4">
          <h2 className="font-heading font-semibold text-base text-forge-text border-b border-forge-border pb-3">
            Competency by Domain
          </h2>

          {data?.progress_by_category && data.progress_by_category.length > 0 ? (
            <div className="space-y-3">
              {data.progress_by_category.map((cat) => {
                const count = cat.solved;
                // Maximum 5 for ratio scale
                const barWidth = Math.min(100, Math.round((count / 5) * 100));

                return (
                  <div key={cat.category} className="space-y-1">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="text-forge-text">{cat.category.replace("_", " ")}</span>
                      <span className="text-forge-cyan font-semibold">{count} Solved</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-forge-bg overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-forge-cyan to-forge-purple rounded-full"
                        style={{ width: `${Math.max(barWidth, 8)}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <EmptyState
              title="No Categorized Solves Yet"
              body="Solve puzzles across Web, Crypto, Forensics, and Reversing to populate your telemetry."
            />
          )}
        </Card>

        {/* Recent Submissions */}
        <Card className="space-y-3">
          <div className="flex items-center justify-between border-b border-forge-border pb-3">
            <h2 className="font-heading font-semibold text-base text-forge-text">Recent Activity Logs</h2>
            <Link to="/submissions" className="text-xs font-mono text-forge-cyan hover:underline">
              All History →
            </Link>
          </div>

          {data?.recent_submissions && data.recent_submissions.length > 0 ? (
            <div className="divide-y divide-forge-border">
              {data.recent_submissions.map((sub) => (
                <div key={sub.id} className="flex items-center justify-between py-2.5 text-xs">
                  <div className="space-y-0.5">
                    <p className="font-medium text-forge-text">{sub.challenge_title}</p>
                    <p className="font-mono text-[10px] text-forge-subtle">
                      {new Date(sub.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </p>
                  </div>
                  <Badge tone={sub.is_correct ? "emerald" : "rose"}>
                    {sub.is_correct ? "Correct" : "Incorrect"}
                  </Badge>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              title="No Activity Logged"
              body="When you submit flags, verification attempts will be recorded here in real time."
            />
          )}
        </Card>
      </div>

      {/* Recommended Challenges Section */}
      <Card className="space-y-4">
        <div className="flex items-center justify-between border-b border-forge-border pb-3">
          <div>
            <h2 className="font-heading font-semibold text-base text-forge-text">Recommended for Your Skill Level</h2>
            <p className="text-xs text-forge-muted">Puzzles tailored to increase your competency profile.</p>
          </div>
          <Link to="/challenges">
            <Button variant="secondary" size="sm" className="gap-1.5">
              <span>View All</span>
              <ArrowRight className="h-3 w-3" />
            </Button>
          </Link>
        </div>

        <div className="grid gap-3 sm:grid-cols-3">
          {(data?.recommended_challenges || []).slice(0, 3).map((c) => (
            <Link
              key={c.id}
              to={`/challenges/${c.id}`}
              className="flex flex-col justify-between rounded-xl border border-forge-border bg-forge-bg/60 p-4 transition hover:border-forge-cyan/40 hover:bg-forge-surface group"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-[10px] text-forge-muted uppercase">{c.category.replace("_", " ")}</span>
                  <Badge tone={difficultyTone(c.difficulty)}>{c.difficulty}</Badge>
                </div>
                <h4 className="font-heading font-semibold text-sm text-forge-text group-hover:text-forge-cyan transition-colors">
                  {c.title}
                </h4>
              </div>
              <div className="mt-4 pt-2 border-t border-forge-border/40 flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-forge-cyan">{c.points} pts</span>
                <span className="text-xs text-forge-muted group-hover:text-forge-cyan flex items-center gap-1 font-mono">
                  Solve →
                </span>
              </div>
            </Link>
          ))}
        </div>
      </Card>
    </div>
  );
}
