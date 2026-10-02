import type { ReactNode } from "react";
import { AlertCircle, CheckCircle2, Info, AlertTriangle } from "lucide-react";

export function Alert({
  children,
  tone = "error",
  className = "",
}: {
  children: ReactNode;
  tone?: "error" | "success" | "info" | "warning";
  className?: string;
}) {
  const styles = {
    success: {
      box: "border-forge-success/30 bg-forge-success/10 text-forge-text",
      icon: <CheckCircle2 className="h-4 w-4 shrink-0 text-forge-success" />,
    },
    info: {
      box: "border-forge-cyan/30 bg-forge-cyan/10 text-forge-text",
      icon: <Info className="h-4 w-4 shrink-0 text-forge-cyan" />,
    },
    warning: {
      box: "border-forge-warning/30 bg-forge-warning/10 text-forge-text",
      icon: <AlertTriangle className="h-4 w-4 shrink-0 text-forge-warning" />,
    },
    error: {
      box: "border-forge-error/30 bg-forge-error/10 text-forge-text",
      icon: <AlertCircle className="h-4 w-4 shrink-0 text-forge-error" />,
    },
  };

  const current = styles[tone];

  return (
    <div className={`flex items-start gap-3 rounded-lg border px-3.5 py-2.5 text-sm ${current.box} ${className}`}>
      {current.icon}
      <div className="leading-snug">{children}</div>
    </div>
  );
}

export function EmptyState({
  title,
  body,
  icon,
  action,
}: {
  title: string;
  body: string;
  icon?: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-forge-border bg-forge-card/40 px-6 py-12 text-center">
      {icon && <div className="mb-3 text-forge-muted">{icon}</div>}
      <p className="font-heading font-semibold text-forge-text">{title}</p>
      <p className="mt-1.5 max-w-sm text-sm text-forge-muted">{body}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function Loading() {
  return (
    <div className="flex items-center justify-center py-12">
      <div className="flex items-center gap-3 text-sm font-mono text-forge-muted">
        <div className="h-4 w-4 animate-spin rounded-full border-2 border-forge-cyan border-t-transparent" />
        <span>INITIALIZING TELEMETRY...</span>
      </div>
    </div>
  );
}

export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded bg-forge-border/40 ${className}`} />;
}
