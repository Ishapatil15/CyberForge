import { useState } from "react";
import { Link } from "react-router-dom";
import {
  Globe,
  Lock,
  FileSearch,
  Cpu,
  Search,
  Shield,
  BookOpen,
  Terminal,
  ExternalLink,
  ChevronRight,
} from "lucide-react";
import { Card } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";

const guides = [
  {
    id: "web",
    title: "Web Security & Client-Side Flaws",
    category: "Web Exploitation",
    icon: Globe,
    difficulty: "EASY",
    overview:
      "Web applications are the most common attack surface. In this track, you learn how browsers interact with APIs, where client-side validation fails, and how parameter tampering occurs.",
    topics: [
      "Distinguishing client-side rendering from server-side security enforcement",
      "Analyzing HTML comments, script bundles, and leaked developer credentials",
      "Parameter manipulation and privilege escalation patterns",
      "SQL Injection: union-based and boolean blind vulnerability patterns",
    ],
    starterChallengeSlug: "login-bypass-primer",
    terminalTip: "curl -I -s https://target.local | grep -i 'set-cookie\\|x-'",
  },
  {
    id: "crypto",
    title: "Applied Cryptography & Cipher Attacks",
    category: "Cryptography",
    icon: Lock,
    difficulty: "EASY",
    overview:
      "Cryptography provides confidentiality, integrity, and authenticity when implemented correctly. Weak entropy, predictable keys, and classical ciphers lead to trivial recoveries.",
    topics: [
      "Caesar & ROT13 frequency analysis and substitution alphabets",
      "XOR cipher properties: A ⊕ B ⊕ B = A and key length derivation",
      "RSA mathematical foundations: modulus N = p*q and Euler totient φ(N)",
      "Modern AES modes: ECB block duplication vs CBC initialization vectors",
    ],
    starterChallengeSlug: "shifted-secrets",
    terminalTip: "echo 'PGS{ebg13}' | tr 'A-Za-z' 'N-ZA-Mn-za-m'",
  },
  {
    id: "forensics",
    title: "Digital Forensics & File Artifacts",
    category: "Digital Forensics",
    icon: FileSearch,
    difficulty: "MEDIUM",
    overview:
      "Forensics operators reconstruct events from memory dumps, disk images, and network captures. Metadata reveals author identity, timestamps, and embedded secrets.",
    topics: [
      "File signatures and Magic Bytes inspection (e.g. 89 50 4E 47 for PNG)",
      "EXIF metadata harvesting from image dumps and PDF document properties",
      "PCAP network packet reconstruction using Wireshark and tshark filters",
      "Hidden data in file slack space and alternate data streams",
    ],
    starterChallengeSlug: "hidden-in-plain-metadata",
    terminalTip: "exiftool image.png | grep -E 'Comment|Description|Author'",
  },
  {
    id: "reversing",
    title: "Static Binary Analysis & Assembly",
    category: "Reverse Engineering",
    icon: Cpu,
    difficulty: "MEDIUM",
    overview:
      "Reverse engineering allows analysts to understand compiled binaries without source code. Discover hardcoded strings, logic branches, and anti-analysis routines.",
    topics: [
      "ELF and PE file structure, symbols, and relocations",
      "Strings extraction from stripped and unstripped executable binaries",
      "x86-64 assembly flow: cmp, jne, test, and calling conventions",
      "Decompilation analysis using Ghidra and IDA Free",
    ],
    starterChallengeSlug: "tiny-password-check",
    terminalTip: "strings -a target.bin | grep -iE 'flag|pass|key|CF{'",
  },
  {
    id: "osint",
    title: "Open Source Intelligence & Reconnaissance",
    category: "OSINT",
    icon: Search,
    difficulty: "EASY",
    overview:
      "OSINT involves ethical intelligence gathering through public databases, social profiles, domain registries, and code repository histories.",
    topics: [
      "Discovering developer aliases across multiple platforms",
      "Git commit history mining for leaked access tokens and passwords",
      "DNS records and historical WHOIS enumeration",
      "Image reverse searching and geolocation mapping",
    ],
    starterChallengeSlug: "campus-handle-hunt",
    terminalTip: "git log -p -S 'secret' --all",
  },
];

export default function LearnPage() {
  const [selectedId, setSelectedId] = useState("web");
  const activeGuide = guides.find((g) => g.id === selectedId) || guides[0];

  return (
    <div className="mx-auto max-w-6xl space-y-8 pb-12">
      <div>
        <div className="flex items-center gap-2">
          <BookOpen className="h-5 w-5 text-forge-cyan" />
          <span className="font-mono text-xs uppercase tracking-wider text-forge-cyan">Field Manual</span>
        </div>
        <h1 className="mt-1 font-heading text-3xl font-bold text-forge-text">
          Security Fundamentals & Lab Guides
        </h1>
        <p className="mt-1 text-sm text-forge-muted">
          Practical writeup frameworks, analytical toolkits, and conceptual foundations for CyberForge challenges.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
        {/* Sidebar Track Selector */}
        <div className="space-y-2">
          {guides.map((g) => {
            const active = g.id === selectedId;
            return (
              <button
                key={g.id}
                onClick={() => setSelectedId(g.id)}
                className={`flex w-full items-center justify-between rounded-xl border p-3.5 text-left transition-all ${
                  active
                    ? "border-forge-cyan/40 bg-forge-card shadow-cyan-sm text-forge-text"
                    : "border-forge-border bg-forge-surface/50 text-forge-muted hover:border-forge-borderHover hover:text-forge-text"
                }`}
              >
                <div className="flex items-center gap-3">
                  <g.icon className={`h-4 w-4 ${active ? "text-forge-cyan" : "text-forge-muted"}`} />
                  <div>
                    <p className="text-sm font-semibold">{g.category}</p>
                    <p className="font-mono text-[10px] text-forge-subtle">{g.difficulty}</p>
                  </div>
                </div>
                <ChevronRight className={`h-4 w-4 ${active ? "text-forge-cyan" : "text-forge-subtle"}`} />
              </button>
            );
          })}
        </div>

        {/* Content Pane */}
        <Card className="space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-forge-border pb-4">
            <div>
              <Badge tone="cyan">{activeGuide.category}</Badge>
              <h2 className="mt-2 font-heading text-2xl font-bold text-forge-text">
                {activeGuide.title}
              </h2>
            </div>
            <Link to="/challenges">
              <Button size="sm">
                <Terminal className="h-3.5 w-3.5" />
                Practice Labs
              </Button>
            </Link>
          </div>

          <div>
            <h3 className="font-mono text-xs uppercase tracking-wider text-forge-muted">Operational Context</h3>
            <p className="mt-2 text-sm text-slate-300 leading-relaxed">{activeGuide.overview}</p>
          </div>

          <div>
            <h3 className="font-mono text-xs uppercase tracking-wider text-forge-muted">Key Learning Objectives</h3>
            <ul className="mt-3 space-y-2 text-sm text-slate-300">
              {activeGuide.topics.map((t, idx) => (
                <li key={idx} className="flex items-start gap-2.5">
                  <span className="font-mono text-xs text-forge-cyan mt-0.5">0{idx + 1}.</span>
                  <span>{t}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Terminal Command Utility Snippet */}
          <div className="rounded-xl border border-forge-border bg-forge-bg p-4 font-mono text-xs">
            <div className="flex items-center justify-between text-forge-muted pb-2 border-b border-forge-border/60">
              <span>CLI INSPECTION SNIPPET</span>
              <span className="text-[10px] text-forge-cyan">SHELL</span>
            </div>
            <p className="mt-3 text-forge-cyan select-all">{activeGuide.terminalTip}</p>
          </div>

          <div className="flex items-center justify-between rounded-xl border border-forge-border bg-forge-surface p-4 text-xs text-forge-muted">
            <span>Ready to apply this technique? Try the starter puzzle in this track:</span>
            <Link to="/challenges" className="font-semibold text-forge-cyan hover:underline flex items-center gap-1">
              Find Challenges <ChevronRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
