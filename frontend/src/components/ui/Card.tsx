import type { ReactNode } from "react";

export function Card({
  children,
  className = "",
  hoverable = false,
}: {
  children: ReactNode;
  className?: string;
  hoverable?: boolean;
}) {
  return (
    <div
      className={`rounded-xl border border-forge-border bg-forge-card p-5 shadow-card ${
        hoverable ? "glow-cyan-hover hover:border-forge-cyan/40 hover:bg-forge-cardHover cursor-pointer" : ""
      } ${className}`}
    >
      {children}
    </div>
  );
}
