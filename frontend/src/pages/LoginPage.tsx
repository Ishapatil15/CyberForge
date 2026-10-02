import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { CyberForgeLogo } from "../components/CyberForgeLogo";
import { api, ApiError } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { Input, Label } from "../components/ui/Field";
import { Alert } from "../components/ui/Feedback";
import { ArrowLeft, KeyRound, ShieldAlert } from "lucide-react";

export default function LoginPage() {
  const { refresh } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setPending(true);
    setError("");
    try {
      await api.post("/api/auth/login", { username, password });
      await refresh();
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Authentication failed");
    } finally {
      setPending(false);
    }
  }

  function setQuickCredentials(u: string, p: string) {
    setUsername(u);
    setPassword(p);
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center px-4 py-12 cyber-grid">
      {/* Ambient background glow */}
      <div className="pointer-events-none absolute left-1/2 top-1/2 -z-10 h-96 w-96 -translate-x-1/2 -translate-y-1/2 rounded-full bg-forge-cyan/10 blur-[120px]" />

      <div className="w-full max-w-md space-y-4">
        <div className="flex items-center justify-between px-1">
          <Link
            to="/"
            className="flex items-center gap-1.5 font-mono text-xs text-forge-muted hover:text-forge-cyan transition-colors"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Return to Homepage
          </Link>
          <span className="font-mono text-[10px] text-forge-cyan">PORTAL // SECURE AUTH</span>
        </div>

        <Card className="border-forge-border bg-forge-card/95 backdrop-blur-md p-6 sm:p-8 shadow-card space-y-6">
          <div className="text-center space-y-2">
            <div className="flex justify-center">
              <CyberForgeLogo />
            </div>
            <h1 className="font-heading text-xl font-bold text-forge-text pt-2">
              Operator Sign In
            </h1>
            <p className="text-xs text-forge-muted">
              Authenticate your identity to submit flags and access live arenas.
            </p>
          </div>

          <form className="space-y-4" onSubmit={onSubmit}>
            {error && <Alert tone="error">{error}</Alert>}

            <div>
              <Label>Operator Username</Label>
              <Input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="operator_handle"
                required
                autoFocus
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <Label className="mb-0">Access Password</Label>
              </div>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                required
              />
            </div>

            <Button className="w-full gap-2 mt-2" disabled={pending}>
              <KeyRound className="h-4 w-4" />
              {pending ? "Authenticating Operator..." : "Authenticate"}
            </Button>
          </form>

          {/* 1-Click Quick Fill Credentials for testing */}
          <div className="rounded-xl border border-forge-border bg-forge-bg/60 p-3.5 space-y-2">
            <div className="flex items-center justify-between text-[11px] font-mono text-forge-muted">
              <span>QUICK DEMO CREDENTIALS</span>
              <span className="text-forge-cyan">CLICK TO FILL</span>
            </div>
            <div className="grid grid-cols-3 gap-1.5">
              <button
                type="button"
                onClick={() => setQuickCredentials("admin", "ChangeMeAdmin!23")}
                className="rounded border border-forge-border bg-forge-surface px-2 py-1 text-center font-mono text-[10px] text-forge-text hover:border-forge-cyan transition-colors"
              >
                Admin
              </button>
              <button
                type="button"
                onClick={() => setQuickCredentials("author", "AuthorPass!23")}
                className="rounded border border-forge-border bg-forge-surface px-2 py-1 text-center font-mono text-[10px] text-forge-text hover:border-forge-cyan transition-colors"
              >
                Author
              </button>
              <button
                type="button"
                onClick={() => setQuickCredentials("isha", "PlayerPass!23")}
                className="rounded border border-forge-border bg-forge-surface px-2 py-1 text-center font-mono text-[10px] text-forge-text hover:border-forge-cyan transition-colors"
              >
                Player (Isha)
              </button>
            </div>
          </div>

          <div className="border-t border-forge-border pt-4 text-center text-xs text-forge-muted">
            Need an operator profile?{" "}
            <Link to="/register" className="font-semibold text-forge-cyan hover:underline">
              Create account
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
