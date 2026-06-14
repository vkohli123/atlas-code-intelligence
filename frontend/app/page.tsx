"use client";

import { useEffect, useState } from "react";
import { Bot, Code2, GitPullRequest, Gauge, Search, ShieldCheck } from "lucide-react";
import { askRepo, indexSampleRepo, listRepos, reviewDiff, type AskResponse, type RepoSummary } from "@/lib/api";
import { Card } from "@/components/Card";

const sampleDiff = `diff --git a/app/services/provider.py b/app/services/provider.py
--- a/app/services/provider.py
+++ b/app/services/provider.py
@@ -1,5 +1,9 @@
+import requests
+
 def call_provider(payload):
+    response = requests.post("https://api.example.com/chat", json=payload)
+    return response.json()
`;

export default function Home() {
  const [repos, setRepos] = useState<RepoSummary[]>([]);
  const [repo, setRepo] = useState("sample-service");
  const [question, setQuestion] = useState("Where is authentication handled?");
  const [answer, setAnswer] = useState<AskResponse | null>(null);
  const [diff, setDiff] = useState(sampleDiff);
  const [review, setReview] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try { setRepos(await listRepos()); } catch { /* backend may still be booting */ }
  }

  useEffect(() => { refresh(); }, []);

  async function handleIndex() {
    setLoading(true); setError(null);
    try { await indexSampleRepo(); await refresh(); setRepo("sample-service"); }
    catch (e: any) { setError(e.message || "Indexing failed"); }
    finally { setLoading(false); }
  }

  async function handleAsk() {
    setLoading(true); setError(null);
    try { setAnswer(await askRepo(repo, question)); }
    catch (e: any) { setError(e.message || "Ask failed"); }
    finally { setLoading(false); }
  }

  async function handleReview() {
    setLoading(true); setError(null);
    try { setReview(await reviewDiff(repo, diff)); }
    catch (e: any) { setError(e.message || "Review failed"); }
    finally { setLoading(false); }
  }

  return (
    <main className="min-h-screen px-6 py-8">
      <section className="mx-auto max-w-7xl space-y-8">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-cyan-400/30 bg-cyan-400/10 px-3 py-1 text-sm text-cyan-200">
              <ShieldCheck size={16} /> Production-grade AI developer tool
            </div>
            <h1 className="text-4xl font-bold tracking-tight text-white md:text-6xl">Atlas</h1>
            <p className="mt-3 max-w-3xl text-lg text-slate-300">
              AI codebase intelligence + PR review agent. Index a repository, ask architecture/code questions with citations, and review diffs like a senior engineer.
            </p>
          </div>
          <button onClick={handleIndex} disabled={loading} className="rounded-xl bg-cyan-400 px-5 py-3 font-semibold text-slate-950 hover:bg-cyan-300 disabled:opacity-50">
            {loading ? "Working..." : "Index sample repo"}
          </button>
        </div>

        {error && <div className="rounded-xl border border-red-400/40 bg-red-500/10 p-4 text-red-200">{error}</div>}

        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <Metric icon={<Code2 />} label="Repos" value={repos.length.toString()} />
          <Metric icon={<Search />} label="Chunks" value={(repos[0]?.chunk_count || 0).toLocaleString()} />
          <Metric icon={<Gauge />} label="LOC" value={(repos[0]?.loc_count || 0).toLocaleString()} />
          <Metric icon={<Bot />} label="Mode" value="Mock/LLM" />
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <div className="mb-4 flex items-center gap-2 text-xl font-semibold text-white"><Search /> Ask the codebase</div>
            <label className="text-sm text-slate-400">Repository</label>
            <input value={repo} onChange={e => setRepo(e.target.value)} className="mt-1 w-full rounded-xl border border-border bg-slate-950 px-3 py-2 text-white" />
            <label className="mt-4 block text-sm text-slate-400">Question</label>
            <textarea value={question} onChange={e => setQuestion(e.target.value)} rows={3} className="mt-1 w-full rounded-xl border border-border bg-slate-950 px-3 py-2 text-white" />
            <button onClick={handleAsk} disabled={loading} className="mt-4 rounded-xl bg-white px-4 py-2 font-semibold text-slate-950 disabled:opacity-50">Ask Atlas</button>
            {answer && (
              <div className="mt-5 space-y-4">
                <div className="rounded-xl bg-slate-950 p-4 text-sm text-slate-200"><pre>{answer.answer}</pre></div>
                <div className="text-xs text-slate-400">Provider: {answer.provider} · Latency: {answer.latency_ms}ms</div>
                <CitationList citations={answer.citations} />
              </div>
            )}
          </Card>

          <Card>
            <div className="mb-4 flex items-center gap-2 text-xl font-semibold text-white"><GitPullRequest /> PR Review Agent</div>
            <label className="text-sm text-slate-400">Diff</label>
            <textarea value={diff} onChange={e => setDiff(e.target.value)} rows={13} className="mt-1 w-full rounded-xl border border-border bg-slate-950 px-3 py-2 font-mono text-xs text-white" />
            <button onClick={handleReview} disabled={loading} className="mt-4 rounded-xl bg-cyan-400 px-4 py-2 font-semibold text-slate-950 disabled:opacity-50">Review PR</button>
            {review && (
              <div className="mt-5 space-y-3">
                <div className="text-sm text-slate-300">{review.summary} · {review.latency_ms}ms</div>
                {review.findings?.map((f: any, i: number) => (
                  <div key={i} className="rounded-xl border border-border bg-slate-950 p-4">
                    <div className="text-sm font-semibold text-white">{f.severity.toUpperCase()} — {f.title}</div>
                    <p className="mt-2 text-sm text-slate-300">{f.rationale}</p>
                    <p className="mt-2 text-sm text-cyan-200">Fix: {f.recommendation}</p>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </section>
    </main>
  );
}

function Metric({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return <Card><div className="flex items-center gap-3 text-slate-400">{icon}<span>{label}</span></div><div className="mt-2 text-3xl font-bold text-white">{value}</div></Card>;
}

function CitationList({ citations }: { citations: any[] }) {
  return <div className="space-y-2">{citations.map((c, i) => (
    <div key={i} className="rounded-xl border border-border bg-slate-900 p-3 text-xs text-slate-300">
      <div className="font-mono text-cyan-200">{c.file_path}:{c.start_line}-{c.end_line} {c.symbol_name ? `· ${c.symbol_name}` : ""}</div>
      <div className="mt-1">score {Number(c.score).toFixed(3)}</div>
      <div className="mt-2 text-slate-400">{c.content_preview}</div>
    </div>
  ))}</div>;
}
