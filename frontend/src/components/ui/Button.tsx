import type { ButtonHTMLAttributes, ReactNode } from "react";

const variants = {
  primary:
    "bg-forge-cyan text-forge-bg hover:brightness-105 active:scale-[0.98] shadow-cyan-sm border border-forge-cyan/20 font-semibold",
  secondary:
    "bg-forge-card text-forge-text border border-forge-border hover:bg-forge-cardHover hover:border-forge-borderHover active:scale-[0.98]",
  purple:
    "bg-forge-purple text-white hover:brightness-110 active:scale-[0.98] shadow-purple border border-forge-purple/30 font-semibold",
  outline:
    "border border-forge-cyan/40 text-forge-cyan hover:bg-forge-cyan/10 active:scale-[0.98]",
  danger:
    "bg-forge-error/15 text-forge-error border border-forge-error/30 hover:bg-forge-error/25 active:scale-[0.98]",
  ghost:
    "text-forge-muted hover:text-forge-text hover:bg-white/5 active:scale-[0.98]",
};

const sizes = {
  sm: "px-3 py-1.5 text-xs rounded-md",
  md: "px-4 py-2 text-sm rounded-lg",
  lg: "px-6 py-2.5 text-base rounded-lg",
};

export function Button({
  variant = "primary",
  size = "md",
  className = "",
  children,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: keyof typeof variants;
  size?: keyof typeof sizes;
  children: ReactNode;
}) {
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 font-medium transition-all duration-150 disabled:pointer-events-none disabled:opacity-50 ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
