import { FormEvent, useEffect, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { api, ApiError } from "../services/api";
import { Badge, difficultyTone } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { Alert, Loading } from "../components/ui/Feedback";
import {
  Terminal,
  Download,
  HelpCircle,
  CheckCircle2,
  AlertCircle,
  Trophy,
  History,
  ArrowLeft,
  KeyRound,
  FileCode,
  ShieldCheck,
  Server,
  Play,
  Square,
  RotateCw,
  ExternalLink,
} from "lucide-react";
import type { Challenge } from "../types";
import { useAuth } from "../hooks/useAuth";

export default function ChallengeDetailPage() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const compId = searchParams.get("competition_id");
  const { refresh } = useAuth();
  const [challenge, setChallenge] = useState<Challenge | null>(null);
  const [flag, setFlag] = useState("");
  const [message, setMessage] = useState<{ tone: "success" | "error" | "info"; text: string } | null>(null);
  const [pending, setPending] = useState(false);
  const [revealingHintId, setRevealingHintId] = useState<number | null>(null);
  const [labStatus, setLabStatus] = useState<{ status: string; target_url: string; port?: number } | null>(null);
  const [labLoading, setLabLoading] = useState(false);

  const isWebLab = Boolean(
    challenge?.slug?.startsWith("lab-") || challenge?.tags?.includes("interactive-lab")
  );
  const labId = challenge?.slug?.startsWith("lab-") ? challenge.slug.replace("lab-", "") : "";

  async function checkLab(targetLabId: string) {
    if (!targetLabId) return;
    try {
      const res = await api.get<{ status: string; target_url: string; port: number }>(`/api/labs/${targetLabId}/status`);
      setLabStatus(res);
    } catch {
      setLabStatus({ status: "STOPPED", target_url: "" });
    }
  }

  async function handleStartLab() {
    if (!labId) return;
    setLabLoading(true);
    try {
      const res = await api.post<{ ok: boolean; status: string; target_url: string; port: number }>(`/api/labs/${labId}/start`);
      setLabStatus(res);
      setMessage({ tone: "info", text: `Web Lab launched at ${res.target_url}` });
    } catch (err) {
      setMessage({ tone: "error", text: err instanceof ApiError ? err.detail : "Failed to launch Web Lab" });
    } finally {
      setLabLoading(false);
    }
  }

  async function handleStopLab() {
    if (!labId) return;
    setLabLoading(true);
    try {
      await api.post(`/api/labs/${labId}/stop`);
      setLabStatus({ status: "STOPPED", target_url: "" });
      setMessage({ tone: "info", text: "Web Lab stopped" });
    } catch (err) {
      setMessage({ tone: "error", text: err instanceof ApiError ? err.detail : "Failed to stop Web Lab" });
    } finally {
      setLabLoading(false);
    }
  }

  async function handleRestartLab() {
    if (!labId) return;
    setLabLoading(true);
    try {
      const res = await api.post<{ ok: boolean; status: string; target_url: string; port: number }>(`/api/labs/${labId}/restart`);
      setLabStatus(res);
      setMessage({ tone: "info", text: `Web Lab restarted at ${res.target_url}` });
    } catch (err) {
      setMessage({ tone: "error", text: err instanceof ApiError ? err.detail : "Failed to restart Web Lab" });
    } finally {
      setLabLoading(false);
    }
  }

  async function load() {
    const data = await api.get<Challenge>(`/api/challenges/${id}`);
    setChallenge(data);
    if (data.slug?.startsWith("lab-")) {
      void checkLab(data.slug.replace("lab-", ""));
    }
  }

  useEffect(() => {
    void load();
  }, [id]);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!flag.trim()) return;
    setPending(true);
    setMessage(null);
    try {
      const payload: { flag: string; competition_id?: number } = { flag: flag.trim() };
      if (compId) {
        payload.competition_id = Number(compId);
      }
      const res = await api.post<{ correct: boolean; already_solved: boolean; points_awarded: number; message: string }>(
        `/api/challenges/${id}/submit`,
        payload
      );

      if (res.correct) {
        setMessage({
          tone: "success",
          text: res.already_solved
            ? "Flag verified! (Challenge already solved previously; no extra points awarded)."
            : `Flag accepted! +${res.points_awarded} Points awarded to your operator profile.`,
        });
      } else {
        setMessage({
          tone: "error",
          text: "Incorrect flag signature. Review the challenge description, decrypt the payload, and try again.",
        });
      }
      setFlag("");
      await load();
      await refresh();
    } catch (err) {
      setMessage({ tone: "error", text: err instanceof ApiError ? err.detail : "Flag submission failed" });
    } finally {
      setPending(false);
    }
  }

  async function reveal(hintId: number) {
    setRevealingHintId(hintId);
    try {
      await api.post(`/api/challenges/${id}/hints/${hintId}/reveal`);
      await load();
      await refresh();
    } catch (err) {
      setMessage({ tone: "error", text: err instanceof ApiError ? err.detail : "Could not reveal hint" });
    } finally {
      setRevealingHintId(null);
    }
  }

  if (!challenge) return <Loading />;

  return (
    <div className="mx-auto max-w-4xl space-y-6 pb-16">
      {/* Back button & Breadcrumb */}
      <div className="flex items-center justify-between">
        <Link
          to={compId ? `/competitions/${compId}` : "/challenges"}
          className="flex items-center gap-1.5 text-xs font-mono text-forge-muted hover:text-forge-cyan transition-colors"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          {compId ? "Back to Competition Event" : "Back to Challenges Matrix"}
        </Link>

        {challenge.solved && (
          <span className="flex items-center gap-1.5 rounded-full border border-forge-success/30 bg-forge-success/10 px-3 py-1 font-mono text-xs font-semibold text-forge-success">
            <CheckCircle2 className="h-3.5 w-3.5" />
            CHALLENGE SOLVED
          </span>
        )}
      </div>

      {/* Active Competition Indicator */}
      {compId && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 rounded-xl border border-forge-cyan/30 bg-forge-cyan/10 p-4 text-xs">
          <div className="flex items-center gap-2.5 text-forge-cyan font-medium">
            <ShieldCheck className="h-4 w-4 shrink-0" />
            <span>Active Competition Mode: Submissions will count directly toward this competition's leaderboard.</span>
          </div>
          <Link to={`/competitions/${compId}`} className="font-mono text-forge-cyan underline font-semibold whitespace-nowrap">
            View Live Standings →
          </Link>
        </div>
      )}

      {/* Title & Metadata Header */}
      <div className="rounded-2xl border border-forge-border bg-forge-card p-6 sm:p-8 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <span className="font-mono text-xs uppercase tracking-wider text-forge-muted">
            {challenge.category.replaceAll("_", " ")}
          </span>
          <div className="flex items-center gap-2">
            <Badge tone={difficultyTone(challenge.difficulty)}>{challenge.difficulty}</Badge>
            <Badge tone="cyan">{challenge.points} PTS</Badge>
            <span className="font-mono text-xs text-forge-muted">
              {challenge.solve_count ?? 0} solves
            </span>
          </div>
        </div>

        <h1 className="font-heading text-3xl sm:text-4xl font-bold text-forge-text">
          {challenge.title}
        </h1>

        {challenge.tags && challenge.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 pt-1">
            {challenge.tags.map((t) => (
              <span
                key={t}
                className="rounded border border-forge-border bg-forge-bg px-2.5 py-0.5 font-mono text-[11px] text-forge-subtle"
              >
                #{t}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Description & Objective */}
      <Card className="space-y-3">
        <h2 className="font-mono text-xs uppercase tracking-wider text-forge-muted">
          Challenge Briefing & Objectives
        </h2>
        <div className="prose prose-invert max-w-none text-sm leading-relaxed text-slate-200">
          <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed bg-transparent p-0 border-0">
            {challenge.description}
          </pre>
        </div>
      </Card>

      {/* Interactive Web Lab Console (if applicable) */}
      {isWebLab && (
        <Card className="space-y-4 border-forge-cyan/40 bg-forge-card shadow-cyan-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5 text-forge-cyan">
              <Server className="h-5 w-5" />
              <h2 className="font-heading text-base font-bold text-forge-text">
                Interactive Target Lab Environment
              </h2>
            </div>
            <div className="flex items-center gap-2">
              <span
                className={`h-2.5 w-2.5 rounded-full ${
                  labStatus?.status === "RUNNING"
                    ? "bg-forge-success shadow-[0_0_8px_rgba(34,197,94,0.7)]"
                    : "bg-slate-600"
                }`}
              />
              <span className="font-mono text-xs uppercase tracking-wider text-slate-300">
                {labStatus?.status || "STOPPED"}
              </span>
            </div>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed">
            This challenge runs an isolated, local vulnerable service. Click <strong>Launch Web Lab</strong> to spin up the target, then access the URL to exploit the vulnerability and extract the flag.
          </p>

          {labStatus?.status === "RUNNING" ? (
            <div className="space-y-3 rounded-lg border border-forge-border bg-forge-surface p-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <div className="font-mono text-xs text-slate-400">Target Address:</div>
                  <a
                    href={labStatus.target_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 font-mono text-sm font-semibold text-forge-cyan hover:underline mt-0.5"
                  >
                    {labStatus.target_url}
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    disabled={labLoading}
                    onClick={() => void handleRestartLab()}
                    className="text-xs gap-1.5"
                  >
                    <RotateCw className="h-3 w-3" />
                    Restart
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    disabled={labLoading}
                    onClick={() => void handleStopLab()}
                    className="text-xs gap-1.5"
                  >
                    <Square className="h-3 w-3" />
                    Stop Lab
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            <Button
              variant="primary"
              disabled={labLoading}
              onClick={() => void handleStartLab()}
              className="w-full gap-2 text-sm font-semibold"
            >
              <Play className="h-4 w-4 fill-current" />
              {labLoading ? "Provisioning Local Lab Instance..." : "Launch Web Lab"}
            </Button>
          )}
        </Card>
      )}

      {/* Files / Attachments */}
      <Card className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="font-mono text-xs uppercase tracking-wider text-forge-muted">
            Target Files & Evidence
          </h2>
          <span className="font-mono text-[11px] text-forge-subtle">
            {challenge.attachments.length} attachment{challenge.attachments.length === 1 ? "" : "s"}
          </span>
        </div>

        {challenge.attachments.length > 0 ? (
          <div className="grid gap-2 sm:grid-cols-2">
            {challenge.attachments.map((a) => (
              <a
                key={a.id}
                href={`/api/challenges/${challenge.id}/attachments/${a.id}`}
                download
                className="flex items-center justify-between rounded-lg border border-forge-border bg-forge-bg/80 p-3 text-sm transition-all hover:border-forge-cyan/40 hover:bg-forge-surface group"
              >
                <div className="flex items-center gap-2.5 overflow-hidden">
                  <FileCode className="h-4 w-4 text-forge-cyan shrink-0" />
                  <span className="truncate font-mono text-xs text-forge-text group-hover:text-forge-cyan transition-colors">
                    {a.original_name}
                  </span>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className="font-mono text-[10px] text-forge-subtle">
                    {Math.round((a.size_bytes / 1024) * 10) / 10} KB
                  </span>
                  <Download className="h-3.5 w-3.5 text-forge-muted group-hover:text-forge-cyan" />
                </div>
              </a>
            ))}
          </div>
        ) : (
          <p className="text-xs text-forge-subtle font-mono">
            No downloadable attachments required for this challenge. Review the description and remote parameters.
          </p>
        )}
      </Card>

      {/* Hints Section */}
      <Card className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <HelpCircle className="h-4 w-4 text-forge-warning" />
            <h2 className="font-mono text-xs uppercase tracking-wider text-forge-muted">
              Intel & Hints
            </h2>
          </div>
          <span className="font-mono text-[11px] text-forge-subtle">
            Penalties apply directly to global points
          </span>
        </div>

        {challenge.hints && challenge.hints.length > 0 ? (
          <div className="space-y-3">
            {challenge.hints.map((h, idx) => (
              <div
                key={h.id}
                className="rounded-xl border border-forge-border bg-forge-bg/60 p-4 transition-all"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs text-forge-text font-medium">
                    Hint #{idx + 1} {h.cost > 0 ? `(−${h.cost} pts)` : "(Free)"}
                  </span>
                  {!h.revealed ? (
                    <Button
                      variant="secondary"
                      size="sm"
                      disabled={revealingHintId === h.id}
                      onClick={() => reveal(h.id)}
                    >
                      {revealingHintId === h.id ? "Unlocking..." : `Unlock Hint ${h.cost > 0 ? `(${h.cost} pts)` : ""}`}
                    </Button>
                  ) : (
                    <Badge tone="cyan">Unlocked</Badge>
                  )}
                </div>

                {h.revealed && (
                  <div className="mt-3 rounded-lg border border-forge-cyan/20 bg-forge-cyan/5 p-3 text-sm text-slate-200 font-sans">
                    {h.content}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-forge-subtle font-mono">No hints recorded for this task.</p>
        )}
      </Card>

      {/* Terminal Flag Submission Field */}
      <div className="rounded-2xl border border-forge-border bg-forge-card p-6 shadow-card space-y-4">
        <div className="flex items-center justify-between border-b border-forge-border pb-3">
          <div className="flex items-center gap-2">
            <Terminal className="h-4 w-4 text-forge-cyan" />
            <span className="font-mono text-xs font-semibold uppercase tracking-wider text-forge-text">
              Flag Submission Terminal
            </span>
          </div>
          <span className="font-mono text-[11px] text-forge-cyan">
            Format: {challenge.flag_format || "CF{...}"}
          </span>
        </div>

        {message && (
          <Alert tone={message.tone === "success" ? "success" : "error"}>
            {message.text}
          </Alert>
        )}

        <form onSubmit={submit} className="space-y-3">
          <div className="relative">
            <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 font-mono text-xs text-forge-cyan">
              &gt;
            </div>
            <input
              type="text"
              placeholder={challenge.flag_format || "CF{your_flag_here}"}
              value={flag}
              onChange={(e) => setFlag(e.target.value)}
              disabled={pending}
              className="w-full rounded-xl border border-forge-border bg-forge-bg pl-8 pr-4 py-3 font-mono text-sm text-forge-cyan placeholder:text-forge-subtle outline-none transition-all focus:border-forge-cyan focus:ring-1 focus:ring-forge-cyan/30"
            />
          </div>

          <div className="flex items-center justify-between pt-1">
            <p className="text-[11px] font-mono text-forge-subtle">
              Press Enter or click Submit. Flag verification runs in constant-time on backend.
            </p>
            <Button disabled={pending || !flag.trim()} size="md" className="gap-2">
              <KeyRound className="h-3.5 w-3.5" />
              {pending ? "Validating Flag..." : "Submit Flag"}
            </Button>
          </div>
        </form>
      </div>

      {/* Previous Attempts History */}
      <Card className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="h-4 w-4 text-forge-muted" />
            <h2 className="font-mono text-xs uppercase tracking-wider text-forge-muted">
              Your Submission Logs
            </h2>
          </div>
          <span className="font-mono text-[11px] text-forge-subtle">
            {challenge.attempts?.length ?? 0} attempt{(challenge.attempts?.length ?? 0) === 1 ? "" : "s"}
          </span>
        </div>

        {challenge.attempts && challenge.attempts.length > 0 ? (
          <div className="divide-y divide-forge-border rounded-lg border border-forge-border overflow-hidden">
            {challenge.attempts.map((a) => (
              <div key={a.id} className="flex items-center justify-between bg-forge-bg/60 p-3 text-xs">
                <span className="font-mono text-forge-muted">
                  {new Date(a.created_at).toLocaleString()}
                </span>
                <Badge tone={a.is_correct ? "emerald" : "rose"}>
                  {a.is_correct ? "Correct Flag" : "Rejected"}
                </Badge>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-forge-subtle font-mono">
            No previous attempts on this puzzle.
          </p>
        )}
      </Card>
    </div>
  );
}
