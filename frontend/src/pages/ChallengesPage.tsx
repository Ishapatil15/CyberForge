import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../services/api";
import { Badge, difficultyTone } from "../components/ui/Badge";
import { Card } from "../components/ui/Card";
import { Input, Select } from "../components/ui/Field";
import { Button } from "../components/ui/Button";
import { EmptyState, Loading } from "../components/ui/Feedback";
import { Terminal, CheckCircle2, Trophy, Search, Filter, ArrowRight } from "lucide-react";
import type { Challenge } from "../types";

const categories = [
  { id: "", label: "All Categories" },
  { id: "WEB", label: "Web" },
  { id: "CRYPTOGRAPHY", label: "Crypto" },
  { id: "FORENSICS", label: "Forensics" },
  { id: "REVERSE_ENGINEERING", label: "Reverse Engineering" },
  { id: "OSINT", label: "OSINT" },
  { id: "BINARY_EXPLOITATION", label: "Pwn" },
  { id: "NETWORKING", label: "Networking" },
  { id: "STEGANOGRAPHY", label: "Stego" },
  { id: "MISCELLANEOUS", label: "Misc" },
];

export default function ChallengesPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [q, setQ] = useState(searchParams.get("q") || "");
  const [category, setCategory] = useState(searchParams.get("category") || "");
  const [difficulty, setDifficulty] = useState(searchParams.get("difficulty") || "");
  const [solved, setSolved] = useState(searchParams.get("solved") || "");
  const [sort, setSort] = useState("newest");
  const [items, setItems] = useState<Challenge[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (category) params.set("category", category);
    if (difficulty) params.set("difficulty", difficulty);
    if (solved) params.set("solved", solved);
    if (sort) params.set("sort", sort);
    setLoading(true);
    api
      .get<{ items: Challenge[] }>(`/api/challenges?${params.toString()}`)
      .then((d) => setItems(d.items))
      .finally(() => setLoading(false));
  }, [q, category, difficulty, solved, sort]);

  return (
    <div className="mx-auto max-w-7xl space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Terminal className="h-5 w-5 text-forge-cyan" />
            <span className="font-mono text-xs uppercase tracking-wider text-forge-cyan">Mission Matrix</span>
          </div>
          <h1 className="mt-1 font-heading text-3xl font-bold text-forge-text">Challenges</h1>
          <p className="mt-1 text-sm text-forge-muted">
            Inspect, reverse engineer, crack, and exploit live cybersecurity puzzles.
          </p>
        </div>
      </div>

      {/* Category Pills Bar */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        {categories.map((c) => {
          const active = category === c.id;
          return (
            <button
              key={c.id}
              onClick={() => setCategory(c.id)}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium whitespace-nowrap transition-all ${
                active
                  ? "border border-forge-cyan/40 bg-forge-cyan/15 text-forge-cyan shadow-cyan-sm"
                  : "border border-forge-border bg-forge-card text-forge-muted hover:border-forge-borderHover hover:text-forge-text"
              }`}
            >
              {c.label}
            </button>
          );
        })}
      </div>

      {/* Filter and Search Bar */}
      <div className="grid gap-3 md:grid-cols-12">
        <div className="relative md:col-span-5">
          <Search className="absolute left-3 top-3 h-4 w-4 text-forge-subtle" />
          <Input
            placeholder="Search by title, description, or CVE tag..."
            value={q}
            onChange={(e) => setQ(e.target.value)}
            className="pl-9"
          />
        </div>
        <div className="md:col-span-3">
          <Select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
            <option value="">All Difficulties</option>
            <option value="EASY">Easy</option>
            <option value="MEDIUM">Medium</option>
            <option value="HARD">Hard</option>
            <option value="EXPERT">Insane / Expert</option>
          </Select>
        </div>
        <div className="md:col-span-2">
          <Select value={solved} onChange={(e) => setSolved(e.target.value)}>
            <option value="">All Statuses</option>
            <option value="false">Unsolved</option>
            <option value="true">Solved</option>
          </Select>
        </div>
        <div className="md:col-span-2">
          <Select value={sort} onChange={(e) => setSort(e.target.value)}>
            <option value="newest">Newest First</option>
            <option value="points">Points (High to Low)</option>
            <option value="difficulty">Difficulty</option>
            <option value="most_solved">Most Solved</option>
          </Select>
        </div>
      </div>

      {/* Grid */}
      {loading ? (
        <Loading />
      ) : items.length === 0 ? (
        <EmptyState
          title="No challenges matched criteria"
          body="Try broadening your search query or reset category and difficulty filters."
          action={
            <Button
              variant="secondary"
              size="sm"
              onClick={() => {
                setQ("");
                setCategory("");
                setDifficulty("");
                setSolved("");
              }}
            >
              Reset Filters
            </Button>
          }
        />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {items.map((c) => (
            <Card key={c.id} hoverable className="flex flex-col justify-between group">
              <div>
                {/* Header row */}
                <div className="flex items-start justify-between gap-3">
                  <div className="space-y-1">
                    <span className="font-mono text-[11px] uppercase tracking-wider text-forge-muted">
                      {c.category.replaceAll("_", " ")}
                    </span>
                    <h3 className="font-heading text-lg font-bold text-forge-text group-hover:text-forge-cyan transition-colors">
                      {c.title}
                    </h3>
                  </div>
                  <div className="flex flex-col items-end gap-1.5">
                    <Badge tone={difficultyTone(c.difficulty)}>{c.difficulty}</Badge>
                    {(c.slug.startsWith("lab-") || c.tags?.includes("interactive-lab")) && (
                      <span className="rounded bg-forge-cyan/15 border border-forge-cyan/30 px-1.5 py-0.5 font-mono text-[9px] font-bold uppercase tracking-wider text-forge-cyan">
                        LIVE LAB
                      </span>
                    )}
                  </div>
                </div>

                {/* Short description */}
                <p className="mt-3 line-clamp-2 text-xs text-forge-muted leading-relaxed">
                  {c.description}
                </p>

                {/* Tags */}
                {c.tags && c.tags.length > 0 && (
                  <div className="mt-3.5 flex flex-wrap gap-1.5">
                    {c.tags.map((t) => (
                      <span
                        key={t}
                        className="rounded border border-forge-border bg-forge-bg px-2 py-0.5 font-mono text-[10px] text-forge-subtle"
                      >
                        #{t}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Bottom metadata & CTA */}
              <div className="mt-5 pt-3.5 border-t border-forge-border flex items-center justify-between">
                <div>
                  <span className="font-mono text-base font-bold text-forge-cyan">
                    {c.points} <span className="text-[10px] font-normal text-forge-muted uppercase">pts</span>
                  </span>
                  <div className="flex items-center gap-1.5 font-mono text-[11px] text-forge-muted mt-0.5">
                    <Trophy className="h-3 w-3 text-forge-subtle" />
                    <span>{c.solve_count ?? 0} solves</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {c.solved ? (
                    <span className="flex items-center gap-1 font-mono text-xs text-forge-success font-medium">
                      <CheckCircle2 className="h-4 w-4" />
                      Solved
                    </span>
                  ) : null}

                  <Link to={`/challenges/${c.id}`}>
                    <Button variant={c.solved ? "secondary" : "primary"} size="sm" className="gap-1.5">
                      <span>{c.solved ? "Review" : "Solve"}</span>
                      <ArrowRight className="h-3 w-3" />
                    </Button>
                  </Link>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
