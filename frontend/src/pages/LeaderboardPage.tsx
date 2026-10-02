import { useEffect, useState } from "react";
import { api } from "../services/api";
import { Card } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { Input, Select } from "../components/ui/Field";
import { Loading } from "../components/ui/Feedback";
import { Trophy, Medal, Search, Swords, Users, Clock, Target } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import type { Competition } from "../types";

type GlobalRow = {
  rank: number;
  user_id: number;
  username: string;
  points: number;
  solves: number;
  attempts?: number;
  accuracy?: string;
  last_score_at?: string | null;
};

export default function LeaderboardPage() {
  const { user } = useAuth();
  const [tab, setTab] = useState<"global" | "competition">("global");
  const [items, setItems] = useState<GlobalRow[]>([]);
  const [competitions, setCompetitions] = useState<Competition[]>([]);
  const [selectedCompId, setSelectedCompId] = useState<string>("");
  const [compBoard, setCompBoard] = useState<Record<string, unknown>[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  // Load global leaderboard & competitions list
  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.get<{ items: GlobalRow[] }>("/api/leaderboard/global"),
      api.get<{ items: Competition[] }>("/api/competitions"),
    ])
      .then(([g, c]) => {
        setItems(g.items || []);
        setCompetitions(c.items || []);
        if (c.items && c.items.length > 0) {
          setSelectedCompId(String(c.items[0].id));
        }
      })
      .finally(() => setLoading(false));
  }, []);

  // Load competition-specific leaderboard when selected
  useEffect(() => {
    if (tab === "competition" && selectedCompId) {
      setLoading(true);
      api
        .get<{ items: Record<string, unknown>[] }>(`/api/competitions/${selectedCompId}/leaderboard`)
        .then((res) => setCompBoard(res.items || []))
        .finally(() => setLoading(false));
    }
  }, [tab, selectedCompId]);

  const filteredGlobal = items.filter((r) =>
    r.username.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="mx-auto max-w-6xl space-y-6 pb-16">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <Trophy className="h-5 w-5 text-forge-cyan" />
          <span className="font-mono text-xs uppercase tracking-wider text-forge-cyan">Standings & Ranks</span>
        </div>
        <h1 className="mt-1 font-heading text-3xl font-bold text-forge-text">Leaderboard</h1>
        <p className="mt-1 text-sm text-forge-muted">
          Real-time deterministic ranking. Ties broken by earliest solve timestamp.
        </p>
      </div>

      {/* Tabs & Controls */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
        {/* Tab switch */}
        <div className="flex items-center gap-1.5 rounded-lg border border-forge-border bg-forge-card p-1">
          <button
            onClick={() => setTab("global")}
            className={`flex items-center gap-2 rounded-md px-3.5 py-1.5 text-xs font-semibold transition-all ${
              tab === "global"
                ? "bg-forge-cyan text-forge-bg shadow-cyan-sm"
                : "text-forge-muted hover:text-forge-text"
            }`}
          >
            <Users className="h-3.5 w-3.5" />
            Global Operators
          </button>
          <button
            onClick={() => setTab("competition")}
            className={`flex items-center gap-2 rounded-md px-3.5 py-1.5 text-xs font-semibold transition-all ${
              tab === "competition"
                ? "bg-forge-cyan text-forge-bg shadow-cyan-sm"
                : "text-forge-muted hover:text-forge-text"
            }`}
          >
            <Swords className="h-3.5 w-3.5" />
            Competition Event
          </button>
        </div>

        {/* Filter inputs */}
        <div className="flex items-center gap-3">
          {tab === "global" ? (
            <div className="relative w-full sm:w-64">
              <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-forge-subtle" />
              <Input
                placeholder="Filter by operator..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-8 py-1.5 text-xs"
              />
            </div>
          ) : (
            <div className="w-full sm:w-72">
              <Select
                value={selectedCompId}
                onChange={(e) => setSelectedCompId(e.target.value)}
                className="py-1.5 text-xs"
              >
                {competitions.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} ({c.status})
                  </option>
                ))}
              </Select>
            </div>
          )}
        </div>
      </div>

      {loading ? (
        <Loading />
      ) : tab === "global" ? (
        /* Global Leaderboard Table */
        <Card className="overflow-x-auto p-0">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-forge-border bg-forge-surface/50 text-[11px] font-mono uppercase text-forge-muted">
              <tr>
                <th className="px-5 py-3.5">Rank</th>
                <th className="px-5 py-3.5">Operator</th>
                <th className="px-5 py-3.5">Total Points</th>
                <th className="px-5 py-3.5">Solves</th>
                <th className="px-5 py-3.5">Accuracy</th>
                <th className="px-5 py-3.5">Last Verified Solve</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-forge-border">
              {filteredGlobal.map((r) => {
                const isMe = user?.id === r.user_id;
                return (
                  <tr
                    key={r.rank}
                    className={`transition-colors ${
                      isMe
                        ? "bg-forge-cyan/10 font-medium text-forge-cyan"
                        : "hover:bg-white/[0.02]"
                    }`}
                  >
                    {/* Rank */}
                    <td className="px-5 py-4 font-mono font-bold">
                      {r.rank === 1 ? (
                        <span className="inline-flex items-center gap-1 text-amber-400">
                          <Medal className="h-4 w-4" /> #1
                        </span>
                      ) : r.rank === 2 ? (
                        <span className="inline-flex items-center gap-1 text-slate-300">
                          <Medal className="h-4 w-4" /> #2
                        </span>
                      ) : r.rank === 3 ? (
                        <span className="inline-flex items-center gap-1 text-amber-600">
                          <Medal className="h-4 w-4" /> #3
                        </span>
                      ) : (
                        <span className="text-forge-muted">#{r.rank}</span>
                      )}
                    </td>

                    {/* Operator */}
                    <td className="px-5 py-4 font-medium">
                      <div className="flex items-center gap-2">
                        <span className="text-forge-text">{r.username}</span>
                        {isMe && <Badge tone="cyan">YOU</Badge>}
                      </div>
                    </td>

                    {/* Points */}
                    <td className="px-5 py-4 font-mono font-bold text-forge-cyan">
                      {r.points} <span className="text-[10px] font-normal text-forge-muted">PTS</span>
                    </td>

                    {/* Solves */}
                    <td className="px-5 py-4 font-mono text-slate-300">
                      {r.solves}
                    </td>

                    {/* Accuracy */}
                    <td className="px-5 py-4 font-mono text-xs text-forge-muted">
                      <span className="inline-flex items-center gap-1">
                        <Target className="h-3 w-3 text-forge-subtle" />
                        {r.accuracy || "100%"}
                      </span>
                    </td>

                    {/* Solve time */}
                    <td className="px-5 py-4 font-mono text-xs text-forge-muted">
                      {r.last_score_at ? (
                        <span className="inline-flex items-center gap-1">
                          <Clock className="h-3 w-3 text-forge-subtle" />
                          {new Date(r.last_score_at).toLocaleString()}
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </Card>
      ) : (
        /* Competition Leaderboard Table */
        <Card className="overflow-x-auto p-0">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-forge-border bg-forge-surface/50 text-[11px] font-mono uppercase text-forge-muted">
              <tr>
                <th className="px-5 py-3.5">Rank</th>
                <th className="px-5 py-3.5">Contender / Squad</th>
                <th className="px-5 py-3.5">Score</th>
                <th className="px-5 py-3.5">Solves</th>
                <th className="px-5 py-3.5">Last Solve Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-forge-border">
              {compBoard.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-sm font-mono text-forge-muted">
                    No verified solves submitted for this competition yet.
                  </td>
                </tr>
              ) : (
                compBoard.map((r) => (
                  <tr key={String(r.rank)} className="hover:bg-white/[0.02]">
                    <td className="px-5 py-4 font-mono font-bold text-forge-cyan">
                      #{String(r.rank)}
                    </td>
                    <td className="px-5 py-4 font-medium text-forge-text">
                      {String(r.username || r.team_name || "—")}
                    </td>
                    <td className="px-5 py-4 font-mono font-bold text-forge-cyan">
                      {String(r.points)} <span className="text-[10px] font-normal text-forge-muted">PTS</span>
                    </td>
                    <td className="px-5 py-4 font-mono text-slate-300">
                      {String(r.solves)}
                    </td>
                    <td className="px-5 py-4 font-mono text-xs text-forge-muted">
                      {r.last_solve_at ? new Date(String(r.last_solve_at)).toLocaleString() : "—"}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  );
}
