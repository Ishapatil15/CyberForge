import { Outlet, Link } from "react-router-dom";
import { Navbar } from "../components/Navbar";
import { CyberForgeLogo } from "../components/CyberForgeLogo";
import { Shield, Terminal, ArrowUpRight, CheckCircle2 } from "lucide-react";

export default function AppLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-forge-bg text-forge-text font-sans selection:bg-forge-cyan/20 selection:text-forge-cyan">
      {/* Top CyberForge Navigation Bar */}
      <Navbar />

      {/* Main Page Workspace */}
      <main className="flex-1 px-4 py-8 sm:px-6 lg:px-8">
        <Outlet />
      </main>

      {/* Technical Cybersecurity Footer */}
      <footer className="border-t border-forge-border bg-forge-surface/60 backdrop-blur-sm mt-auto text-xs text-forge-muted">
        <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-5">
            {/* Brand column */}
            <div className="space-y-3 lg:col-span-2">
              <CyberForgeLogo />
              <p className="max-w-sm text-xs text-forge-muted leading-relaxed">
                CyberForge is a modern cybersecurity training and competition platform engineered for universities,
                enterprise red/blue teams, and independent ethical security researchers.
              </p>
              <div className="flex items-center gap-2 pt-1 font-mono text-[11px] text-forge-cyan">
                <span className="flex h-2 w-2 rounded-full bg-forge-cyan animate-pulse" />
                <span>OPERATIONAL // ALL SYSTEMS GREEN</span>
              </div>
            </div>

            {/* Quick Links: Platform */}
            <div className="space-y-2.5">
              <p className="font-mono text-xs font-semibold uppercase tracking-wider text-forge-text">
                Platform
              </p>
              <ul className="space-y-1.5 text-xs">
                <li>
                  <Link to="/challenges" className="hover:text-forge-cyan transition-colors">
                    Challenge Matrix
                  </Link>
                </li>
                <li>
                  <Link to="/competitions" className="hover:text-forge-cyan transition-colors">
                    Wargame Arenas
                  </Link>
                </li>
                <li>
                  <Link to="/leaderboard" className="hover:text-forge-cyan transition-colors">
                    Global Standings
                  </Link>
                </li>
                <li>
                  <Link to="/teams" className="hover:text-forge-cyan transition-colors">
                    Squads & Teams
                  </Link>
                </li>
              </ul>
            </div>

            {/* Quick Links: Resources */}
            <div className="space-y-2.5">
              <p className="font-mono text-xs font-semibold uppercase tracking-wider text-forge-text">
                Resources
              </p>
              <ul className="space-y-1.5 text-xs">
                <li>
                  <Link to="/learn" className="hover:text-forge-cyan transition-colors">
                    Security Field Manual
                  </Link>
                </li>
                <li>
                  <Link to="/about" className="hover:text-forge-cyan transition-colors">
                    Rules of Engagement
                  </Link>
                </li>
                <li>
                  <a
                    href="/api/docs"
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 hover:text-forge-cyan transition-colors"
                  >
                    API Telemetry Docs <ArrowUpRight className="h-3 w-3 text-forge-subtle" />
                  </a>
                </li>
              </ul>
            </div>

            {/* Security Notice */}
            <div className="space-y-2.5">
              <p className="font-mono text-xs font-semibold uppercase tracking-wider text-forge-text">
                Security Notice
              </p>
              <p className="text-[11px] text-forge-subtle leading-relaxed">
                All platform challenges are conducted in simulated and safe environments. Unauthorized attacks against external systems or platform servers are strictly prohibited.
              </p>
              <span className="inline-flex items-center gap-1 font-mono text-[10px] text-forge-success">
                <CheckCircle2 className="h-3 w-3" /> Constant-time HMAC Verification
              </span>
            </div>
          </div>

          <div className="mt-10 border-t border-forge-border pt-6 flex flex-col sm:flex-row items-center justify-between gap-4 font-mono text-[11px] text-forge-subtle">
            <p>© 2026 CyberForge Security Labs. Professional CTF & Cybersecurity Training.</p>
            <p>SERVER TIMESTAMP: {new Date().toISOString().slice(0, 10)} UTC</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
