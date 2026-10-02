import type { InputHTMLAttributes, TextareaHTMLAttributes, SelectHTMLAttributes, ReactNode } from "react";

const baseField =
  "w-full rounded-lg border border-forge-border bg-forge-bg/90 px-3.5 py-2.5 text-sm text-forge-text outline-none transition-all placeholder:text-forge-subtle focus:border-forge-cyan focus:ring-1 focus:ring-forge-cyan/30 disabled:opacity-50 font-sans";

export function Input({ className = "", ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return <input className={`${baseField} ${className}`} {...props} />;
}

export function Textarea({ className = "", ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className={`${baseField} min-h-28 resize-y ${className}`} {...props} />;
}

export function Select({ className = "", children, ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select className={`${baseField} cursor-pointer bg-[#0D1422] ${className}`} {...props}>
      {children}
    </select>
  );
}

export function Label({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <label className={`mb-1.5 block text-xs font-mono uppercase tracking-wider text-forge-muted ${className}`}>
      {children}
    </label>
  );
}
