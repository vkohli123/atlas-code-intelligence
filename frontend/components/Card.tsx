export function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <div className={`rounded-2xl border border-border bg-panel/80 p-5 shadow-2xl shadow-black/20 ${className}`}>{children}</div>;
}
