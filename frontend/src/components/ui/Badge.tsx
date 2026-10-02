import type { ReactNode } from "react";

const tones = {
  cyan: "bg-[#00D9FF]/10 text-[#00D9FF] border-[#00D9FF]/30",
  purple: "bg-[#7C3AED]/15 text-[#C084FC] border-[#7C3AED]/30",
  amber: "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/30",
  rose: "bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/30",
  emerald: "bg-[#22C55E]/10 text-[#22C55E] border-[#22C55E]/30",
  insane: "bg-[#A855F7]/15 text-[#D8B4FE] border-[#A855F7]/30",
  slate: "bg-[#1E293B]/70 text-[#94A3B8] border-[#1E293B]",
};

export function Badge({
  children,
  tone = "slate",
  className = "",
}: {
  children: ReactNode;
  tone?: keyof typeof tones;
  className?: string;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-md border px-2.5 py-0.5 text-xs font-mono font-medium tracking-tight ${tones[tone]} ${className}`}
    >
      {children}
    </span>
  );
}

export function difficultyTone(d: string) {
  const norm = d.toUpperCase();
  if (norm === "EASY") return "emerald" as const;
  if (norm === "MEDIUM") return "amber" as const;
  if (norm === "HARD") return "rose" as const;
  if (norm === "INSANE" || norm === "EXPERT") return "insane" as const;
  return "slate" as const;
}
