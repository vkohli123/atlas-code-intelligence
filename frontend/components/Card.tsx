export function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <div className={`rounded-[2rem] border border-stone-200 bg-white p-5 shadow-sm ${className}`}>{children}</div>;
}
