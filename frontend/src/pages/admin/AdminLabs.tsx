import { useEffect, useState } from "react";
import { api, ApiError } from "../../services/api";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Badge, difficultyTone } from "../../components/ui/Badge";
import { Alert, Loading } from "../../components/ui/Feedback";
import { Server, Play, Square, RotateCw, ExternalLink, ShieldAlert, Cpu } from "lucide-react";

interface LabItem {
  id: string;
  name: string;
  category: string;
  port: number;
  target_url: string;
  challenge_slug: string;
  description: string;
  difficulty: "EASY" | "MEDIUM" | "HARD" | "EXPERT";
  points: number;
  status: "RUNNING" | "STOPPED";
  uptime_seconds: number;
  timeout_seconds: number;
}

export default function AdminLabs() {
  const [labs, setLabs] = useState<LabItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionPending, setActionPending] = useState<string | null>(null);
  const [alert, setAlert] = useState<{ tone: "success" | "error"; text: string } | null>(null);

  async function loadLabs() {
    try {
      const res = await api.get<{ items: LabItem[] }>("/api/labs");
      setLabs(res.items);
    } catch (err) {
      setAlert({ tone: "error", text: err instanceof ApiError ? err.detail : "Failed to load labs" });
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadLabs();
    const interval = setInterval(loadLabs, 5000);
    return () => clearInterval(interval);
  }, []);

  async function startLab(id: string) {
    setActionPending(id);
    setAlert(null);
    try {
      await api.post(`/api/labs/${id}/start`);
      setAlert({ tone: "success", text: `Lab ${id} started successfully.` });
      await loadLabs();
    } catch (err) {
      setAlert({ tone: "error", text: err instanceof ApiError ? err.detail : "Failed to start lab" });
    } finally {
      setActionPending(null);
    }
  }

  async function stopLab(id: string) {
    setActionPending(id);
    setAlert(null);
    try {
      await api.post(`/api/labs/${id}/stop`);
      setAlert({ tone: "success", text: `Lab ${id} stopped.` });
      await loadLabs();
    } catch (err) {
      setAlert({ tone: "error", text: err instanceof ApiError ? err.detail : "Failed to stop lab" });
    } finally {
      setActionPending(null);
    }
  }

  async function restartLab(id: string) {
    setActionPending(id);
    setAlert(null);
    try {
      await api.post(`/api/labs/${id}/restart`);
      setAlert({ tone: "success", text: `Lab ${id} restarted.` });
      await loadLabs();
    } catch (err) {
      setAlert({ tone: "error", text: err instanceof ApiError ? err.detail : "Failed to restart lab" });
    } finally {
      setActionPending(null);
    }
  }

  if (loading) return <Loading />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-forge-border pb-4">
        <div>
          <h2 className="font-heading text-xl font-bold text-forge-text">Interactive Web Labs Management</h2>
          <p className="text-sm text-slate-400">
            Control local isolated vulnerable applications used for live student exploitation exercises.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => void loadLabs()} className="gap-2">
          <RotateCw className="h-4 w-4" />
          Refresh Status
        </Button>
      </div>

      {alert && <Alert tone={alert.tone}>{alert.text}</Alert>}

      <div className="grid gap-4 md:grid-cols-3">
        {labs.map((lab) => {
          const isRunning = lab.status === "RUNNING";
          const pending = actionPending === lab.id;

          return (
            <Card key={lab.id} className="flex flex-col justify-between space-y-4 border-forge-border bg-forge-card p-5">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span
                      className={`h-2.5 w-2.5 rounded-full ${
                        isRunning ? "bg-forge-success shadow-[0_0_8px_rgba(34,197,94,0.6)]" : "bg-slate-600"
                      }`}
                    />
                    <span className="font-mono text-xs font-semibold uppercase tracking-wider text-slate-300">
                      {lab.status}
                    </span>
                  </div>
                  <Badge tone={difficultyTone(lab.difficulty)}>{lab.difficulty}</Badge>
                </div>

                <div className="space-y-1">
                  <h3 className="font-heading text-base font-bold text-forge-text">{lab.name}</h3>
                  <p className="text-xs leading-relaxed text-slate-400">{lab.description}</p>
                </div>

                <div className="rounded-lg border border-forge-border bg-forge-surface/60 p-2.5 space-y-1.5 font-mono text-xs">
                  <div className="flex justify-between text-slate-400">
                    <span>Target Port:</span>
                    <span className="text-forge-cyan">{lab.port}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Assigned Points:</span>
                    <span className="text-slate-200">{lab.points} PTS</span>
                  </div>
                  {isRunning && (
                    <div className="flex justify-between text-slate-400">
                      <span>Uptime:</span>
                      <span className="text-forge-success">{lab.uptime_seconds}s</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="space-y-2 pt-2 border-t border-forge-border">
                {isRunning ? (
                  <div className="space-y-2">
                    <a
                      href={lab.target_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-center gap-2 rounded-lg bg-forge-cyan/15 px-3 py-2 text-xs font-semibold text-forge-cyan border border-forge-cyan/30 hover:bg-forge-cyan/25 transition-colors w-full"
                    >
                      <ExternalLink className="h-3.5 w-3.5" />
                      Open Target ({lab.target_url})
                    </a>
                    <div className="flex gap-2">
                      <Button
                        variant="danger"
                        size="sm"
                        disabled={pending}
                        onClick={() => void stopLab(lab.id)}
                        className="flex-1 gap-1.5 text-xs"
                      >
                        <Square className="h-3 w-3" />
                        Stop
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        disabled={pending}
                        onClick={() => void restartLab(lab.id)}
                        className="flex-1 gap-1.5 text-xs"
                      >
                        <RotateCw className="h-3 w-3" />
                        Restart
                      </Button>
                    </div>
                  </div>
                ) : (
                  <Button
                    variant="primary"
                    size="sm"
                    disabled={pending}
                    onClick={() => void startLab(lab.id)}
                    className="w-full gap-2 text-xs"
                  >
                    <Play className="h-3.5 w-3.5 fill-current" />
                    Launch Web Lab
                  </Button>
                )}
              </div>
            </Card>
          );
        })}
      </div>

      {/* Deployment & Docker Architecture Card */}
      <Card className="space-y-3 border-forge-border bg-forge-card p-6">
        <div className="flex items-center gap-2.5 text-forge-cyan">
          <Cpu className="h-5 w-5" />
          <h3 className="font-heading text-sm font-bold text-forge-text">Lab Architecture & Container Specs</h3>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          Labs run in isolated sandboxed processes on designated loopback ports (8011, 8012, 8013).
          For production or Docker Compose orchestration, run:
        </p>
        <pre className="rounded-lg border border-forge-border bg-forge-bg p-3 font-mono text-xs text-forge-cyan overflow-x-auto">
          cd "d:\CTF Platform\web-labs" &amp;&amp; docker compose up -d
        </pre>
      </Card>
    </div>
  );
}
