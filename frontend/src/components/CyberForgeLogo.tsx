import { Link } from "react-router-dom";

export function CyberForgeLogo({
  className = "",
  showTagline = true,
  size = "md",
}: {
  className?: string;
  showTagline?: boolean;
  size?: "sm" | "md" | "lg";
}) {
  const iconSizes = {
    sm: "h-7 w-auto",
    md: "h-9 w-auto",
    lg: "h-11 w-auto",
  };

  const textSizes = {
    sm: "text-base",
    md: "text-lg",
    lg: "text-xl",
  };

  return (
    <Link to="/" className={`group flex items-center gap-2.5 transition-opacity hover:opacity-95 ${className}`}>
      {/* Isolated Transparent CyberForge Emblem */}
      <img
        src="/cyberforge-logo.png"
        alt="CyberForge Emblem"
        className={`${iconSizes[size]} object-contain drop-shadow-[0_0_10px_rgba(0,217,255,0.3)] transition-transform duration-200 group-hover:scale-105`}
      />
      <div className="flex flex-col leading-tight">
        <span className={`font-heading font-extrabold tracking-wide text-white ${textSizes[size]}`}>
          CYBER<span className="text-[#00D9FF]">FORGE</span>
        </span>
        {showTagline && (
          <span className="font-mono text-[9px] font-semibold uppercase tracking-widest text-slate-400">
            CTF PLATFORM
          </span>
        )}
      </div>
    </Link>
  );
}
