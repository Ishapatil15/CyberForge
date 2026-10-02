import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { CyberForgeLogo } from "../components/CyberForgeLogo";
import { api, ApiError } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { Input, Label } from "../components/ui/Field";
import { Alert } from "../components/ui/Feedback";
import { ArrowLeft, UserPlus } from "lucide-react";

export default function RegisterPage() {
  const { refresh } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setPending(true);
    setError("");
    try {
      await api.post("/api/auth/register", { username, email, password });
      await refresh();
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Registration failed");
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center px-4 py-12 cyber-grid">
      {/* Ambient background glow */}
      <div className="pointer-events-none absolute left-1/2 top-1/2 -z-10 h-96 w-96 -translate-x-1/2 -translate-y-1/2 rounded-full bg-forge-purple/10 blur-[120px]" />

      <div className="w-full max-w-md space-y-4">
        <div className="flex items-center justify-between px-1">
          <Link
            to="/"
            className="flex items-center gap-1.5 font-mono text-xs text-forge-muted hover:text-forge-cyan transition-colors"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Return to Homepage
          </Link>
          <span className="font-mono text-[10px] text-forge-purple">PORTAL // NEW OPERATOR</span>
        </div>

        <Card className="border-forge-border bg-forge-card/95 backdrop-blur-md p-6 sm:p-8 shadow-card space-y-6">
          <div className="text-center space-y-2">
            <div className="flex justify-center">
              <CyberForgeLogo />
            </div>
            <h1 className="font-heading text-xl font-bold text-forge-text pt-2">
              Register Operator Account
            </h1>
            <p className="text-xs text-forge-muted">
              Enroll your cybersecurity handle to participate in arenas and track telemetry.
            </p>
          </div>

          <form className="space-y-4" onSubmit={onSubmit}>
            {error && <Alert tone="error">{error}</Alert>}

            <div>
              <Label>Handle / Username (3-32 characters)</Label>
              <Input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="cyber_operator"
                required
                autoFocus
              />
            </div>

            <div>
              <Label>Email Address</Label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="operator@domain.local"
                required
              />
            </div>

            <div>
              <Label>Access Password (Min 8 characters)</Label>
              <Input
                type="password"
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                required
              />
            </div>

            <Button className="w-full gap-2 mt-2" disabled={pending}>
              <UserPlus className="h-4 w-4" />
              {pending ? "Creating Account..." : "Create Account"}
            </Button>
          </form>

          <div className="border-t border-forge-border pt-4 text-center text-xs text-forge-muted">
            Already registered?{" "}
            <Link to="/login" className="font-semibold text-forge-cyan hover:underline">
              Sign In
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
