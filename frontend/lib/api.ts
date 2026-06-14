export type Citation = {
  file_path: string;
  start_line: number;
  end_line: number;
  symbol_name?: string | null;
  score: number;
  content_preview: string;
};

export type AskResponse = {
  answer: string;
  citations: Citation[];
  latency_ms: number;
  provider: string;
};

export type RepoSummary = {
  name: string;
  source_url?: string | null;
  file_count: number;
  chunk_count: number;
  loc_count: number;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function listRepos(): Promise<RepoSummary[]> {
  const res = await fetch(`${API_BASE}/api/repos`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to list repositories");
  return res.json();
}

export async function indexSampleRepo(): Promise<unknown> {
  const res = await fetch(`${API_BASE}/api/repos/index-local`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: "sample-service", path: "/app/examples/sample-service" })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function askRepo(repo: string, question: string): Promise<AskResponse> {
  const res = await fetch(`${API_BASE}/api/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo, question, top_k: 8 })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function reviewDiff(repo: string, diff: string) {
  const res = await fetch(`${API_BASE}/api/pr-review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo, diff, top_k: 8 })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
