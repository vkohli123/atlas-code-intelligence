"use client";

import { useEffect, useMemo, useState } from "react";
import {
  ArrowUpRight,
  Bot,
  CheckCircle2,
  Code2,
  FileCode2,
  GitPullRequest,
  Loader2,
  Search,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import {
  askRepo,
  indexSampleRepo,
  listRepos,
  reviewDiff,
  type AskResponse,
  type RepoSummary,
} from "@/lib/api";

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

const examplePrompts = [
  "Where is provider fallback implemented?",
  "Where is request cost calculated?",
  "How does semantic caching work?",
  "What reliability risks exist in this codebase?",
];

export default function Home() {
  const [repos, setRepos] = useState<RepoSummary[]>([]);
  const [repo, setRepo] = useState("sample-service");
  const [question, setQuestion] = useState("Where is provider logic implemented?");
  const [answer, setAnswer] = useState<AskResponse | null>(null);
  const [diff, setDiff] = useState(sampleDiff);
  const [review, setReview] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"ask" | "review">("ask");
  const [error, setError] = useState<string | null>(null);

  const selectedRepo = useMemo(
    () => repos.find((item) => item.name === repo) || repos[0],
    [repos, repo],
  );

  async function refresh() {
    try {
      const data = await listRepos();
      setRepos(data);
      if (!data.find((item) => item.name === repo) && data[0]?.name) {
        setRepo(data[0].name);
      }
    } catch {
      // Backend may still be booting.
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function withLoading(task: () => Promise<void>) {
    setLoading(true);
    setError(null);
    try {
      await task();
    } catch (e: any) {
      setError(e?.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  function handleIndex() {
    withLoading(async () => {
      await indexSampleRepo();
      await refresh();
      setRepo("sample-service");
    });
  }

  function handleAsk() {
    withLoading(async () => {
      setAnswer(await askRepo(repo, question));
    });
  }

  function handleReview() {
    withLoading(async () => {
      setReview(await reviewDiff(repo, diff));
    });
  }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,#eef2ff,transparent_34%),linear-gradient(180deg,#fbfbf8,#f5f6f2)] text-stone-950">
      <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-5 py-6 sm:px-8 lg:px-10">
        <header className="flex items-center justify-between border-b border-stone-200/80 pb-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-stone-950 text-white shadow-sm">
              <Sparkles size={18} />
            </div>
            <div>
              <div className="text-lg font-semibold tracking-tight">Atlas</div>
              <div className="text-xs text-stone-500">AI Codebase Intelligence</div>
            </div>
          </div>
          <div className="hidden items-center gap-2 rounded-full border border-stone-200 bg-white/70 px-3 py-1.5 text-xs text-stone-600 shadow-sm backdrop-blur sm:flex">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            Mock/LLM mode
          </div>
        </header>

        <section className="grid flex-1 gap-10 py-10 lg:grid-cols-[0.95fr_1.05fr] lg:items-start lg:py-14">
          <aside className="space-y-8">
            <div className="space-y-5">
              <div className="inline-flex items-center gap-2 rounded-full border border-stone-200 bg-white/80 px-3 py-1.5 text-xs font-medium text-stone-600 shadow-sm">
                <ShieldCheck size={14} />
                Source-grounded developer AI
              </div>
              <div className="space-y-4">
                <h1 className="max-w-xl text-5xl font-semibold tracking-[-0.055em] text-stone-950 sm:text-6xl lg:text-7xl">
                  Navigate any codebase.
                </h1>
                <p className="max-w-2xl text-base leading-7 text-stone-600 sm:text-lg">
                  Ask architecture questions, inspect implementation paths, and review diffs with cited code evidence.
                </p>
              </div>
            </div>

            <div className="rounded-[2rem] border border-stone-200 bg-white/80 p-4 shadow-[0_28px_80px_rgba(15,23,42,0.08)] backdrop-blur">
              <div className="grid gap-3 sm:grid-cols-3">
                <Stat label="Repositories" value={(repos.length || 0).toLocaleString()} />
                <Stat label="Chunks" value={(selectedRepo?.chunk_count || 0).toLocaleString()} />
                <Stat label="LOC" value={(selectedRepo?.loc_count || 0).toLocaleString()} />
              </div>
              <div className="mt-4 flex flex-wrap gap-2 text-xs text-stone-500">
                <span className="rounded-full bg-stone-100 px-3 py-1">pgvector retrieval</span>
                <span className="rounded-full bg-stone-100 px-3 py-1">Redis cache</span>
                <span className="rounded-full bg-stone-100 px-3 py-1">FastAPI</span>
                <span className="rounded-full bg-stone-100 px-3 py-1">Next.js</span>
              </div>
            </div>

            <div className="rounded-[2rem] border border-stone-200 bg-white/70 p-5 shadow-sm backdrop-blur">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <div className="text-sm font-semibold text-stone-950">Workspace</div>
                  <div className="text-xs text-stone-500">Choose an indexed repository or sync the demo repo.</div>
                </div>
                <button
                  onClick={handleIndex}
                  disabled={loading}
                  className="inline-flex items-center gap-2 rounded-full bg-stone-950 px-4 py-2 text-xs font-semibold text-white shadow-sm transition hover:bg-stone-800 disabled:opacity-50"
                >
                  {loading ? <Loader2 className="animate-spin" size={14} /> : <ArrowUpRight size={14} />}
                  Index sample
                </button>
              </div>
              <label className="text-xs font-medium uppercase tracking-[0.18em] text-stone-400">Repository</label>
              <input
                value={repo}
                onChange={(e) => setRepo(e.target.value)}
                className="mt-2 w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-sm font-medium text-stone-900 outline-none transition placeholder:text-stone-400 focus:border-stone-400 focus:ring-4 focus:ring-stone-200/70"
                placeholder="llm-gateway"
              />
              {repos.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {repos.slice(0, 5).map((item) => (
                    <button
                      key={item.name}
                      onClick={() => setRepo(item.name)}
                      className={`rounded-full border px-3 py-1 text-xs transition ${repo === item.name ? "border-stone-950 bg-stone-950 text-white" : "border-stone-200 bg-white text-stone-600 hover:border-stone-300"}`}
                    >
                      {item.name}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </aside>

          <section className="rounded-[2.5rem] border border-stone-200 bg-white p-3 shadow-[0_36px_100px_rgba(15,23,42,0.12)]">
            <div className="rounded-[2rem] border border-stone-100 bg-[#fbfbf8] p-2">
              <div className="grid grid-cols-2 gap-2 rounded-full bg-stone-100 p-1 text-sm font-medium text-stone-500">
                <button
                  onClick={() => setActiveTab("ask")}
                  className={`rounded-full px-4 py-2.5 transition ${activeTab === "ask" ? "bg-white text-stone-950 shadow-sm" : "hover:text-stone-800"}`}
                >
                  Ask Atlas
                </button>
                <button
                  onClick={() => setActiveTab("review")}
                  className={`rounded-full px-4 py-2.5 transition ${activeTab === "review" ? "bg-white text-stone-950 shadow-sm" : "hover:text-stone-800"}`}
                >
                  Review PR
                </button>
              </div>
            </div>

            {error && (
              <div className="mx-3 mt-4 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                {error}
              </div>
            )}

            {activeTab === "ask" ? (
              <AskPanel
                question={question}
                setQuestion={setQuestion}
                answer={answer}
                loading={loading}
                onAsk={handleAsk}
                onPrompt={(prompt) => {
                  setQuestion(prompt);
                  setActiveTab("ask");
                }}
              />
            ) : (
              <ReviewPanel diff={diff} setDiff={setDiff} review={review} loading={loading} onReview={handleReview} />
            )}
          </section>
        </section>
      </div>
    </main>
  );
}

function AskPanel({
  question,
  setQuestion,
  answer,
  loading,
  onAsk,
  onPrompt,
}: {
  question: string;
  setQuestion: (value: string) => void;
  answer: AskResponse | null;
  loading: boolean;
  onAsk: () => void;
  onPrompt: (prompt: string) => void;
}) {
  return (
    <div className="space-y-6 p-4 sm:p-6">
      <div className="rounded-[1.75rem] border border-stone-200 bg-white p-3 shadow-sm">
        <div className="flex items-start gap-3">
          <div className="mt-2 flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-stone-950 text-white">
            <Search size={18} />
          </div>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={3}
            className="min-h-[90px] flex-1 resize-none bg-transparent px-1 py-2 text-lg font-medium leading-7 text-stone-950 outline-none placeholder:text-stone-400"
            placeholder="Ask how a feature works, where logic lives, or what files should change..."
          />
        </div>
        <div className="mt-3 flex flex-col gap-3 border-t border-stone-100 pt-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-wrap gap-2">
            {examplePrompts.slice(0, 2).map((prompt) => (
              <button key={prompt} onClick={() => onPrompt(prompt)} className="rounded-full bg-stone-100 px-3 py-1.5 text-xs text-stone-600 transition hover:bg-stone-200">
                {prompt}
              </button>
            ))}
          </div>
          <button
            onClick={onAsk}
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 rounded-full bg-stone-950 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-stone-800 disabled:opacity-50"
          >
            {loading ? <Loader2 className="animate-spin" size={16} /> : <Sparkles size={16} />}
            Ask
          </button>
        </div>
      </div>

      {answer ? (
        <div className="grid gap-4 xl:grid-cols-[1.12fr_0.88fr]">
          <div className="rounded-[1.75rem] border border-stone-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div>
                <div className="text-xs font-medium uppercase tracking-[0.18em] text-stone-400">Answer</div>
                <div className="mt-1 text-sm text-stone-500">Grounded in retrieved code regions</div>
              </div>
              <div className="rounded-full border border-stone-200 bg-stone-50 px-3 py-1 text-xs text-stone-500">
                {answer.latency_ms}ms · {answer.provider}
              </div>
            </div>
            <pre className="whitespace-pre-wrap break-words rounded-3xl bg-stone-950 p-5 text-sm leading-7 text-stone-100 shadow-inner">
              {answer.answer}
            </pre>
          </div>
          <EvidencePanel citations={answer.citations || []} />
        </div>
      ) : (
        <div className="rounded-[1.75rem] border border-dashed border-stone-300 bg-white/70 p-8 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-stone-950 text-white">
            <Code2 size={20} />
          </div>
          <h2 className="mt-4 text-xl font-semibold tracking-tight text-stone-950">Start with a code question.</h2>
          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-stone-500">
            Atlas will retrieve relevant files, functions, and snippets, then return a cited answer you can verify.
          </p>
          <div className="mt-5 flex flex-wrap justify-center gap-2">
            {examplePrompts.map((prompt) => (
              <button key={prompt} onClick={() => onPrompt(prompt)} className="rounded-full border border-stone-200 bg-white px-3 py-1.5 text-xs text-stone-600 transition hover:border-stone-300 hover:bg-stone-50">
                {prompt}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function ReviewPanel({
  diff,
  setDiff,
  review,
  loading,
  onReview,
}: {
  diff: string;
  setDiff: (value: string) => void;
  review: any;
  loading: boolean;
  onReview: () => void;
}) {
  return (
    <div className="grid gap-5 p-4 sm:p-6 xl:grid-cols-[1.05fr_0.95fr]">
      <div className="rounded-[1.75rem] border border-stone-200 bg-white p-5 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 text-sm font-semibold text-stone-950">
              <GitPullRequest size={16} /> PR diff
            </div>
            <div className="mt-1 text-xs text-stone-500">Paste a diff and Atlas will review risk with retrieved context.</div>
          </div>
          <button
            onClick={onReview}
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-full bg-stone-950 px-4 py-2 text-xs font-semibold text-white shadow-sm transition hover:bg-stone-800 disabled:opacity-50"
          >
            {loading ? <Loader2 className="animate-spin" size={14} /> : <Bot size={14} />}
            Review
          </button>
        </div>
        <textarea
          value={diff}
          onChange={(e) => setDiff(e.target.value)}
          rows={17}
          className="w-full resize-none rounded-3xl border border-stone-900 bg-[#050505] p-4 font-mono text-xs leading-6 text-stone-100 outline-none ring-offset-2 transition placeholder:text-stone-500 focus:ring-4 focus:ring-stone-300"
        />
      </div>

      <div className="rounded-[1.75rem] border border-stone-200 bg-white p-5 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <div className="text-xs font-medium uppercase tracking-[0.18em] text-stone-400">Review findings</div>
            <div className="mt-1 text-sm text-stone-500">Concise, hunk-level feedback</div>
          </div>
          {review?.latency_ms !== undefined && <div className="rounded-full bg-stone-100 px-3 py-1 text-xs text-stone-500">{review.latency_ms}ms</div>}
        </div>
        {review ? (
          <div className="space-y-3">
            <p className="rounded-2xl bg-stone-50 p-3 text-sm leading-6 text-stone-600">{review.summary}</p>
            {review.findings?.map((finding: any, index: number) => (
              <div key={index} className="rounded-3xl border border-stone-200 bg-white p-4 shadow-sm">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2 text-sm font-semibold text-stone-950">
                    <CheckCircle2 size={16} className="text-amber-500" />
                    {finding.title}
                  </div>
                  <span className="rounded-full bg-stone-950 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide text-white">
                    {finding.severity}
                  </span>
                </div>
                <p className="mt-3 text-sm leading-6 text-stone-600">{finding.rationale}</p>
                <p className="mt-3 rounded-2xl bg-emerald-50 p-3 text-sm leading-6 text-emerald-800">
                  Fix: {finding.recommendation}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex h-[430px] flex-col items-center justify-center rounded-3xl border border-dashed border-stone-300 bg-stone-50/70 p-8 text-center">
            <FileCode2 size={26} className="text-stone-400" />
            <h3 className="mt-4 text-lg font-semibold tracking-tight text-stone-950">No review yet.</h3>
            <p className="mt-2 max-w-sm text-sm leading-6 text-stone-500">
              Run the review agent to produce prioritized findings, risk labels, and implementation guidance.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function EvidencePanel({ citations }: { citations: any[] }) {
  return (
    <div className="rounded-[1.75rem] border border-stone-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <div className="text-xs font-medium uppercase tracking-[0.18em] text-stone-400">Evidence</div>
          <div className="mt-1 text-sm text-stone-500">{citations.length} retrieved regions</div>
        </div>
        <Search size={16} className="text-stone-400" />
      </div>
      <div className="max-h-[520px] space-y-3 overflow-auto pr-1">
        {citations.map((citation, index) => (
          <div key={`${citation.file_path}-${index}`} className="rounded-3xl border border-stone-200 bg-stone-50/80 p-4">
            <div className="flex items-start justify-between gap-3">
              <div className="font-mono text-xs font-semibold text-stone-950">
                {citation.file_path}:{citation.start_line}-{citation.end_line}
              </div>
              <div className="rounded-full bg-white px-2 py-1 text-[10px] text-stone-500 shadow-sm">
                {Number(citation.score || 0).toFixed(2)}
              </div>
            </div>
            {citation.symbol_name && <div className="mt-2 text-xs font-medium text-stone-500">{citation.symbol_name}</div>}
            <p className="mt-3 line-clamp-4 text-xs leading-5 text-stone-600">{citation.content_preview}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-3xl bg-stone-50 p-4">
      <div className="text-xs font-medium uppercase tracking-[0.16em] text-stone-400">{label}</div>
      <div className="mt-2 text-2xl font-semibold tracking-tight text-stone-950">{value}</div>
    </div>
  );
}
