import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import { Badge } from "../components/ui/Badge";
import { Card } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { EmptyState, Loading } from "../components/ui/Feedback";
import { Swords, Calendar, Users, Flag, ArrowRight, ShieldCheck } from "lucide-react";
import type { Competition } from "../types";

export default function CompetitionsPage() {
  const [items, setItems] = useState<Competition[] | null>(null);

  useEffect(() => {
    api.get<{ items: Competition[] }>("/api/competitions").then((d) => setItems(d.items));
  }, []);

  if (!items) return <Loading />;

  return (
    <div className="mx-auto max-w-6xl space-y-6 pb-16">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <Swords className="h-5 w-5 text-forge-cyan" />
          <span className="font-mono text-xs uppercase tracking-wider text-forge-cyan">Wargame Arenas</span>
        </div>
        <h1 className="mt-1 font-heading text-3xl font-bold text-forge-text">Competitions</h1>
        <p className="mt-1 text-sm text-forge-muted">
          Scheduled competitive events with server-enforced time windows and live leaderboards.
        </p>
      </div>

      {items.length === 0 ? (
        <EmptyState
          title="No Active Competitions"
          body="Competition organizers can schedule new events from the administrative console."
        />
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          {items.map((c) => {
            const isActive = c.status === "ACTIVE";
            const isRegOpen = c.status === "REGISTRATION_OPEN";
            const statusTone = isActive ? "cyan" : isRegOpen ? "amber" : "slate";

            return (
              <Card
                key={c.id}
                hoverable
                className={`flex flex-col justify-between transition-all ${
                  isActive ? "border-forge-cyan/40 shadow-cyan-sm" : ""
                }`}
              >
                <div className="space-y-4">
                  {/* Top row */}
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        {isActive && <span className="h-2 w-2 rounded-full bg-forge-cyan animate-pulse" />}
                        <h2 className="font-heading text-xl font-bold text-forge-text">{c.name}</h2>
                      </div>
                      <span className="font-mono text-[11px] text-forge-muted uppercase tracking-wider">
                        {c.mode} MODE {c.registration_required ? "• REGISTRATION REQUIRED" : "• OPEN"}
                      </span>
                    </div>
                    <Badge tone={statusTone}>{c.status.replace("_", " ")}</Badge>
                  </div>

                  {/* Description */}
                  <p className="text-xs text-forge-muted leading-relaxed line-clamp-3">
                    {c.description}
                  </p>

                  {/* Metrics grid */}
                  <div className="grid grid-cols-2 gap-2 rounded-lg border border-forge-border bg-forge-bg/60 p-3 font-mono text-xs">
                    <div className="flex items-center gap-2 text-forge-muted">
                      <Flag className="h-3.5 w-3.5 text-forge-cyan" />
                      <span>{c.challenge_count} Challenges</span>
                    </div>
                    <div className="flex items-center gap-2 text-forge-muted">
                      <Users className="h-3.5 w-3.5 text-forge-purple" />
                      <span>{c.participant_count} Participants</span>
                    </div>
                  </div>

                  {/* Dates */}
                  <div className="flex items-center gap-2 font-mono text-[11px] text-forge-subtle">
                    <Calendar className="h-3.5 w-3.5" />
                    <span>
                      {new Date(c.start_at).toLocaleDateString()} {new Date(c.start_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      {" → "}
                      {new Date(c.end_at).toLocaleDateString()} {new Date(c.end_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </div>

                {/* Footer CTA */}
                <div className="mt-6 pt-4 border-t border-forge-border flex items-center justify-between">
                  <div className="text-xs font-mono">
                    {c.registered ? (
                      <span className="flex items-center gap-1.5 text-forge-success font-semibold">
                        <ShieldCheck className="h-4 w-4" /> Registered
                      </span>
                    ) : (
                      <span className="text-forge-muted">
                        {isActive ? "Live in Progress" : "Available to join"}
                      </span>
                    )}
                  </div>

                  <Link to={`/competitions/${c.id}`}>
                    <Button variant={isActive ? "primary" : "secondary"} size="sm" className="gap-1.5">
                      <span>{isActive ? "Enter Arena" : "View Details"}</span>
                      <ArrowRight className="h-3.5 w-3.5" />
                    </Button>
                  </Link>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
