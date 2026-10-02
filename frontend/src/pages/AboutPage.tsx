import { Shield, Terminal, CheckCircle2, AlertOctagon, Lock, Cpu, Server } from "lucide-react";
import { Card } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";

export default function AboutPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-10 pb-16">
      <div>
        <div className="flex items-center gap-2">
          <Shield className="h-5 w-5 text-forge-cyan" />
          <span className="font-mono text-xs uppercase tracking-wider text-forge-cyan">Architecture & Rules</span>
        </div>
        <h1 className="mt-1 font-heading text-3xl font-bold text-forge-text sm:text-4xl">
          About CyberForge
        </h1>
        <p className="mt-2 text-sm text-forge-muted">
          A modern, high-performance cybersecurity training and CTF platform designed for realistic student competitions, universities, and ethical hacking teams.
        </p>
      </div>

      {/* Core Mission */}
      <Card className="space-y-3">
        <h2 className="font-heading text-xl font-bold text-forge-text">Platform Philosophy</h2>
        <p className="text-sm text-slate-300 leading-relaxed">
          CyberForge was built from the ground up to replace outdated, visually cluttered CTF frameworks with a professional, SaaS-quality platform. We prioritize server-side security enforcement, cryptographic verification, and accurate time synchronization so competitions remain fair, robust, and demonstrable.
        </p>
      </Card>

      {/* Rules of Engagement */}
      <Card className="space-y-4">
        <div className="flex items-center gap-2">
          <AlertOctagon className="h-5 w-5 text-forge-warning" />
          <h2 className="font-heading text-xl font-bold text-forge-text">Rules of Engagement</h2>
        </div>
        <p className="text-sm text-forge-muted">
          All participants must strictly abide by ethical competition conduct:
        </p>
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-lg border border-forge-border bg-forge-bg p-3.5 text-xs text-slate-300 space-y-1">
            <span className="font-mono text-forge-cyan font-semibold">01 // NO PLATFORM ATTACKS</span>
            <p className="text-forge-muted">
              Do not attempt to attack, overwhelm, or denial-of-service the CyberForge application server or database. Rate limits are strictly enforced.
            </p>
          </div>
          <div className="rounded-lg border border-forge-border bg-forge-bg p-3.5 text-xs text-slate-300 space-y-1">
            <span className="font-mono text-forge-cyan font-semibold">02 // NO FLAG SHARING</span>
            <p className="text-forge-muted">
              Collaboration is permitted only within registered teams. Sharing flags or solutions between competing squads is strictly prohibited.
            </p>
          </div>
          <div className="rounded-lg border border-forge-border bg-forge-bg p-3.5 text-xs text-slate-300 space-y-1">
            <span className="font-mono text-forge-cyan font-semibold">03 // SELF-CONTAINED TARGETS</span>
            <p className="text-forge-muted">
              All challenge tasks and files are self-contained puzzles. Do not run automated fuzzers or port scanners against third-party public IPs.
            </p>
          </div>
          <div className="rounded-lg border border-forge-border bg-forge-bg p-3.5 text-xs text-slate-300 space-y-1">
            <span className="font-mono text-forge-cyan font-semibold">04 // FAIR REPORTING</span>
            <p className="text-forge-muted">
              If you identify an infrastructure vulnerability, report it immediately to administrators via responsible disclosure.
            </p>
          </div>
        </div>
      </Card>

      {/* Technical Specifications */}
      <Card className="space-y-4">
        <h2 className="font-heading text-xl font-bold text-forge-text">Security Specifications</h2>
        <div className="space-y-3 text-sm text-slate-300">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="h-4 w-4 text-forge-cyan mt-1 shrink-0" />
            <div>
              <p className="font-semibold text-forge-text">HMAC-SHA256 Salted Verification</p>
              <p className="text-xs text-forge-muted">
                Flags are hashed with a server-side pepper and verified using constant-time digest comparison (`hmac.compare_digest`), preventing timing leak attacks.
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <CheckCircle2 className="h-4 w-4 text-forge-cyan mt-1 shrink-0" />
            <div>
              <p className="font-semibold text-forge-text">Argon2 Password Hashing</p>
              <p className="text-xs text-forge-muted">
                Operator credentials are protected with Argon2 password hashing algorithms with memory and cost parameters.
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <CheckCircle2 className="h-4 w-4 text-forge-cyan mt-1 shrink-0" />
            <div>
              <p className="font-semibold text-forge-text">Deterministic Tie-Breaking Engine</p>
              <p className="text-xs text-forge-muted">
                Leaderboard ranks evaluate total points first, broken deterministically by the earliest solve timestamp.
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <CheckCircle2 className="h-4 w-4 text-forge-cyan mt-1 shrink-0" />
            <div>
              <p className="font-semibold text-forge-text">Hardened Upload Storage</p>
              <p className="text-xs text-forge-muted">
                Attachments undergo extension whitelisting, MIME validation, UUID storage renaming, and path traversal prevention.
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
