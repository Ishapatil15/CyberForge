import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Shield,
  Terminal,
  Trophy,
  Swords,
  Globe,
  Lock,
  Cpu,
  Search,
  FileSearch,
  Radio,
  ArrowRight,
  Flame,
  CheckCircle,
} from "lucide-react";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { api } from "../services/api";
import { useAuth } from "../hooks/useAuth";

type PlatformStats = {
  active_challenges: number;
  registered_players: number;
  competitions: number;
  challenges_solved: number;
};

const domains = [
  {
    name: "Web Exploitation",
    desc: "SQL injections, session bypasses, SSRF, XSS, and broken access controls.",
    icon: Globe,
    count: "10+ Labs",
    accent: "text-forge-cyan",
  },
  {
    name: "Cryptography",
    desc: "Cipher analysis, RSA factoring, block cipher modes, and discrete logarithms.",
    icon: Lock,
    count: "8+ Labs",
    accent: "text-forge-purple",
  },
  {
    name: "Digital Forensics",
    desc: "Memory image analysis, PCAP packet inspection, disk recovery, and file metadata.",
    icon: FileSearch,
    count: "6+ Labs",
    accent: "text-forge-cyan",
  },
  {
    name: "Reverse Engineering",
    desc: "Disassembly, ELF/PE inspection, static binary analysis, and anti-debug evasion.",
    icon: Cpu,
    count: "7+ Labs",
    accent: "text-forge-purple",
  },
  {
    name: "OSINT & Intelligence",
    desc: "Open source reconnaissance, geo-location, metadata mining, and credential analysis.",
    icon: Search,
    count: "5+ Labs",
    accent: "text-forge-cyan",
  },
  {
    name: "Binary Exploitation (Pwn)",
    desc: "Stack buffer overflows, ROP chain execution, format string vulnerabilities.",
    icon: Terminal,
    count: "6+ Labs",
    accent: "text-forge-purple",
  },
];

export default function HomePage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<PlatformStats>({
    active_challenges: 5,
    registered_players: 6,
    competitions: 1,
    challenges_solved: 8,
  });

  useEffect(() => {
    api
      .get<PlatformStats>("/api/stats")
      .then(setStats)
      .catch(() => {
        // Fallback to default
      });
  }, []);

  return (
    <div className="space-y-20 pb-16">
      {/* Hero Section with cyber grid & subtle ambient glow */}
      <section className="relative overflow-hidden pt-12 pb-16 sm:pt-20 sm:pb-24">
        {/* Ambient Glows */}
        <div className="pointer-events-none absolute -top-24 left-1/2 -z-10 h-96 w-96 -translate-x-1/2 rounded-full bg-forge-cyan/10 blur-[120px]" />
        <div className="pointer-events-none absolute top-40 right-10 -z-10 h-72 w-72 rounded-full bg-forge-purple/10 blur-[100px]" />

        <div className="cyber-grid absolute inset-0 -z-20 opacity-30" />

        <div className="mx-auto max-w-5xl text-center px-4">
          {/* Subtle Tagline */}
          <div className="inline-flex items-center gap-2 rounded-full border border-forge-border bg-forge-card/80 px-3.5 py-1 text-xs font-mono text-forge-muted backdrop-blur-sm">
            <span className="flex h-2 w-2 rounded-full bg-forge-cyan animate-pulse" />
            CYBERSECURITY COMPETITION & LAB PLATFORM
          </div>

          <h1 className="mt-6 font-heading text-4xl font-extrabold tracking-tight text-forge-text sm:text-6xl lg:text-7xl">
            CYBER<span className="text-forge-cyan">FORGE</span>
            <span className="block mt-2 text-2xl sm:text-4xl lg:text-5xl font-bold text-slate-300">
              Forge Your Security Skills.
            </span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-base text-forge-muted sm:text-lg">
            Practice real-world cybersecurity through hands-on challenges, competitions, and security labs.
            Server-side flag validation, deterministic leaderboards, and zero simulated compromises.
          </p>

          {/* Action CTAs */}
          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link to="/challenges">
              <Button size="lg" className="gap-2.5">
                <Terminal className="h-4 w-4" />
                Explore Challenges
              </Button>
            </Link>
            <Link to="/leaderboard">
              <Button variant="secondary" size="lg" className="gap-2.5">
                <Trophy className="h-4 w-4 text-forge-muted" />
                View Leaderboard
              </Button>
            </Link>
          </div>

          {/* Verification Badges */}
          <div className="mt-12 flex flex-wrap items-center justify-center gap-6 text-xs font-mono text-forge-subtle">
            <span className="flex items-center gap-1.5">
              <CheckCircle className="h-3.5 w-3.5 text-forge-success" />
              HMAC Server-Side Validation
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle className="h-3.5 w-3.5 text-forge-cyan" />
              Real-Time UTC Clocks
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle className="h-3.5 w-3.5 text-forge-purple" />
              Team & Individual Modes
            </span>
          </div>
        </div>
      </section>

      {/* Platform Statistics Section */}
      <section className="mx-auto max-w-6xl px-4">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <Card className="text-center py-6 glow-cyan-hover">
            <p className="font-mono text-xs uppercase tracking-wider text-forge-muted">Active Challenges</p>
            <p className="mt-2 font-mono text-3xl sm:text-4xl font-bold text-forge-cyan">
              {stats.active_challenges}
            </p>
          </Card>
          <Card className="text-center py-6 glow-cyan-hover">
            <p className="font-mono text-xs uppercase tracking-wider text-forge-muted">Registered Players</p>
            <p className="mt-2 font-mono text-3xl sm:text-4xl font-bold text-forge-text">
              {stats.registered_players}
            </p>
          </Card>
          <Card className="text-center py-6 glow-cyan-hover">
            <p className="font-mono text-xs uppercase tracking-wider text-forge-muted">Competitions</p>
            <p className="mt-2 font-mono text-3xl sm:text-4xl font-bold text-forge-purple">
              {stats.competitions}
            </p>
          </Card>
          <Card className="text-center py-6 glow-cyan-hover">
            <p className="font-mono text-xs uppercase tracking-wider text-forge-muted">Challenges Solved</p>
            <p className="mt-2 font-mono text-3xl sm:text-4xl font-bold text-forge-success">
              {stats.challenges_solved}
            </p>
          </Card>
        </div>
      </section>

      {/* Live Competition Banner Preview */}
      <section className="mx-auto max-w-6xl px-4">
        <div className="relative overflow-hidden rounded-2xl border border-forge-cyan/30 bg-gradient-to-r from-forge-card via-forge-surface to-forge-card p-6 sm:p-8 shadow-card">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="flex h-2.5 w-2.5 rounded-full bg-forge-cyan animate-ping" />
                <Badge tone="cyan">LIVE COMPETITION</Badge>
                <span className="font-mono text-xs text-forge-muted">CYBER WARFARE 2026</span>
              </div>
              <h3 className="font-heading text-xl sm:text-2xl font-bold text-forge-text">
                Annual University Invitational CTF
              </h3>
              <p className="max-w-xl text-sm text-forge-muted">
                Compete against top university operators in Web, Reverse Engineering, Cryptography, and Forensics.
                Points count directly toward the global and competition standings.
              </p>
            </div>
            <Link to="/competitions/1">
              <Button size="lg" className="whitespace-nowrap">
                <Swords className="h-4 w-4" />
                Enter Competition
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Security Domains & Skill Tracks */}
      <section className="mx-auto max-w-6xl px-4 space-y-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-end justify-between gap-4">
          <div>
            <span className="font-mono text-xs uppercase tracking-wider text-forge-cyan">Skill Tracks</span>
            <h2 className="font-heading text-2xl sm:text-3xl font-bold text-forge-text">
              Master Modern Attack & Defense
            </h2>
          </div>
          <Link to="/challenges" className="flex items-center gap-1.5 text-sm font-medium text-forge-cyan hover:underline">
            Browse all categories <ArrowRight className="h-4 w-4" />
          </Link>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {domains.map((d) => (
            <Card key={d.name} hoverable className="flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className={`p-2.5 rounded-lg border border-forge-border bg-forge-bg ${d.accent}`}>
                    <d.icon className="h-5 w-5" />
                  </div>
                  <Badge tone="slate">{d.count}</Badge>
                </div>
                <h3 className="font-heading font-semibold text-forge-text">{d.name}</h3>
                <p className="mt-1.5 text-xs text-forge-muted leading-relaxed">{d.desc}</p>
              </div>
              <div className="mt-4 pt-3 border-t border-forge-border/60 flex items-center justify-between">
                <span className="text-xs font-mono text-forge-subtle">STANDALONE PUZZLE</span>
                <Link to="/challenges" className="text-xs font-medium text-forge-cyan hover:underline flex items-center gap-1">
                  Start <ArrowRight className="h-3 w-3" />
                </Link>
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* CyberForge Operational Principles */}
      <section className="mx-auto max-w-6xl px-4">
        <div className="rounded-2xl border border-forge-border bg-forge-surface p-8 sm:p-12">
          <div className="text-center max-w-2xl mx-auto space-y-3">
            <span className="font-mono text-xs uppercase text-forge-purple tracking-widest">
              ENGINEERED FOR INTEGRITY
            </span>
            <h2 className="font-heading text-2xl sm:text-3xl font-bold text-forge-text">
              How CyberForge Works
            </h2>
            <p className="text-sm text-forge-muted">
              Built by cybersecurity engineers for realistic student competitions and professional skill benchmarking.
            </p>
          </div>

          <div className="mt-12 grid gap-6 sm:grid-cols-3">
            <div className="space-y-2.5 rounded-xl border border-forge-border/80 bg-forge-card p-5">
              <div className="font-mono text-xs text-forge-cyan">01 // TARGET</div>
              <h4 className="font-heading font-semibold text-forge-text">Hands-On Investigation</h4>
              <p className="text-xs text-forge-muted leading-relaxed">
                Download packet captures, analyze stripped binaries, investigate obfuscated web endpoints, and inspect memory dumps.
              </p>
            </div>
            <div className="space-y-2.5 rounded-xl border border-forge-border/80 bg-forge-card p-5">
              <div className="font-mono text-xs text-forge-cyan">02 // VERIFY</div>
              <h4 className="font-heading font-semibold text-forge-text">Server-Side Validation</h4>
              <p className="text-xs text-forge-muted leading-relaxed">
                Flags are evaluated strictly by backend cryptographic digests. No client-side leaks, no plaintext exposure in DevTools.
              </p>
            </div>
            <div className="space-y-2.5 rounded-xl border border-forge-border/80 bg-forge-card p-5">
              <div className="font-mono text-xs text-forge-cyan">03 // SCORE</div>
              <h4 className="font-heading font-semibold text-forge-text">Deterministic Ranking</h4>
              <p className="text-xs text-forge-muted leading-relaxed">
                Atomic score updates with hint penalties accounted for. Deterministic tie-breaking rules reward precision and speed.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="mx-auto max-w-5xl px-4 text-center">
        <div className="rounded-2xl border border-forge-border bg-gradient-to-b from-forge-card to-forge-bg p-8 sm:p-12">
          <h2 className="font-heading text-3xl font-bold text-forge-text sm:text-4xl">
            Ready to test your defenses?
          </h2>
          <p className="mx-auto mt-3 max-w-lg text-sm text-forge-muted">
            Create an operator account, join a squad, or immediately dive into published challenges.
          </p>
          <div className="mt-6 flex flex-wrap justify-center gap-3">
            <Link to={user ? "/challenges" : "/register"}>
              <Button size="lg">{user ? "Browse Challenges" : "Create Free Account"}</Button>
            </Link>
            <Link to="/about">
              <Button variant="secondary" size="lg">Platform Architecture</Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
